import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Logo } from "@/components/Logo";
import { StepProgress } from "@/components/StepProgress";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, ArrowLeft, Loader2, Check, RefreshCw, Image as ImageIcon, Edit } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Textarea } from "@/components/ui/textarea";

const steps = [
  { number: 1, title: "Summarize" },
  { number: 2, title: "Prompts" },
  { number: 3, title: "Images" },
  { number: 4, title: "Video" },
];

interface GeneratedImage {
  id: string;
  promptId: string;
  scene: string;
  imageUrl: string;
  approved: boolean;
  isGenerating: boolean;
}

export default function Step3Images() {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const prompts = location.state?.prompts || [];
  const storyData = location.state?.storyData || null;
  const [images, setImages] = useState<GeneratedImage[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImageData, setGeneratedImageData] = useState<any[]>([]);
  const [modifyingImageId, setModifyingImageId] = useState<string | null>(null);
  const [userInputs, setUserInputs] = useState<{ [key: string]: string }>({});

  const handleGenerateAll = async () => {
    setIsGenerating(true);
    const newImages: GeneratedImage[] = prompts.map((prompt: any) => ({
      id: `img-${prompt.id}`,
      promptId: prompt.id,
      scene: prompt.scene,
      imageUrl: "",
      approved: false,
      isGenerating: true,
    }));
    setImages(newImages);

    try {
      const { imageApi } = await import("@/lib/api");
      
      // Backend expects story_data as an array of scene objects
      // Use the storyData from Step2 if available, otherwise construct from prompts
      let storyScenes = [];
      if (storyData && storyData.scenes) {
        storyScenes = storyData.scenes;
      } else {
        // Fallback: construct basic scene data from prompts
        storyScenes = prompts.map((prompt: any) => ({
          scene: prompt.scene,
          narration: prompt.description,
          visual_cues: prompt.description,
          prompts: [prompt.description]
        }));
      }
      
      const response = await imageApi.generate({ story_data: storyScenes });
      
      // Check if the backend response indicates success
      if (response.data && !response.data.success) {
        throw new Error(response.data.message || "Failed to generate images");
      }
      
      // Backend returns: { success, message, data: { images: [...] }, status_code }
      // Axios puts it in response.data, so we access response.data.data.images
      const responseData = response.data.data || response.data;
      const imagesData = responseData.images || [];
      
      // Store the full image data for later use
      setGeneratedImageData(imagesData);
      
      // Convert backend image paths to accessible URLs
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      const generatedImages = imagesData.map((img: any, index: number) => {
        let imageUrl = img.image || img.url || img.image_url || "";
        
        // If it's a local file path, convert to API URL
        if (imageUrl && !imageUrl.startsWith('http')) {
          // Remove any leading slashes and ensure proper path
          const cleanPath = imageUrl.replace(/^\/+/, '').replace(/\\/g, '/');
          imageUrl = `${API_BASE_URL}/${cleanPath}`;
        }
        
        console.log('Image URL:', imageUrl); // Debug log
        
        return {
          id: img.id || `img-${index}`,
          promptId: img.scene_id || prompts[index]?.id,
          scene: img.scene || prompts[index]?.scene,
          imageUrl: imageUrl,
          approved: false,
          isGenerating: false,
        };
      });
      
      setImages(generatedImages);
      toast({
        title: "Images Generated",
        description: "All scene images have been created successfully.",
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          "Failed to generate images";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleApprove = (id: string) => {
    setImages(images.map(img => img.id === id ? { ...img, approved: !img.approved } : img));
  };

  const handleRegenerate = async (id: string) => {
    setImages(images.map(img => 
      img.id === id ? { ...img, isGenerating: true } : img
    ));
    
    try {
      const { imageApi } = await import("@/lib/api");
      
      // Find the corresponding scene data for this image
      const imageIndex = images.findIndex(img => img.id === id);
      const sceneData = generatedImageData[imageIndex] || storyData?.scenes?.[imageIndex] || {
        scene: images[imageIndex]?.scene || "Scene",
        narration: images[imageIndex]?.scene || "",
        visual_cues: images[imageIndex]?.scene || "",
        prompts: [images[imageIndex]?.scene || ""]
      };
      
      const response = await imageApi.regenerate({ scene_data: sceneData });
      
      // Check if the backend response indicates success
      if (response.data && !response.data.success) {
        throw new Error(response.data.message || "Failed to regenerate image");
      }
      
      // Backend returns: { success, message, data: { image: "...", ... }, status_code }
      // Axios puts it in response.data, so we access response.data.data.image
      const responseData = response.data.data || response.data;
      let imageUrl = responseData.image || responseData.url || responseData.image_url || "";
      
      // Convert backend image path to accessible URL
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      if (imageUrl && !imageUrl.startsWith('http')) {
        const cleanPath = imageUrl.replace(/^\/+/, '').replace(/\\/g, '/');
        imageUrl = `${API_BASE_URL}/${cleanPath}`;
      }
      
      console.log('Regenerated Image URL:', imageUrl); // Debug log
      
      // Update the generatedImageData as well
      const newImageData = [...generatedImageData];
      newImageData[imageIndex] = responseData;
      setGeneratedImageData(newImageData);
      
      setImages(images.map(img => 
        img.id === id ? { 
          ...img, 
          imageUrl: imageUrl, 
          isGenerating: false 
        } : img
      ));
      toast({
        title: "Image Regenerated",
        description: "New image has been generated for this scene.",
      });
    } catch (error: any) {
      setImages(images.map(img => 
        img.id === id ? { ...img, isGenerating: false } : img
      ));
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          "Failed to regenerate image";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  const handleModifyImage = async (id: string) => {
    const userInput = userInputs[id];
    
    if (!userInput || !userInput.trim()) {
      toast({
        title: "No Changes Specified",
        description: "Please enter your requested changes first.",
        variant: "destructive",
      });
      return;
    }
    
    setModifyingImageId(id);
    setImages(images.map(img => 
      img.id === id ? { ...img, isGenerating: true } : img
    ));
    
    try {
      const { imageApi } = await import("@/lib/api");
      
      // Find the corresponding scene data for this image
      const imageIndex = images.findIndex(img => img.id === id);
      const sceneData = generatedImageData[imageIndex] || storyData?.scenes?.[imageIndex] || {
        scene: images[imageIndex]?.scene || "Scene",
        narration: images[imageIndex]?.scene || "",
        visual_cues: images[imageIndex]?.scene || "",
        prompts: [images[imageIndex]?.scene || ""]
      };
      
      // Call the modify image endpoint
      const response = await imageApi.modifyImage({
        scene_data: sceneData,
        user_input: userInput
      });
      
      // Check if the backend response indicates success
      if (response.data && !response.data.success) {
        throw new Error(response.data.message || "Failed to modify image");
      }
      
      const responseData = response.data.data || response.data;
      let imageUrl = responseData.image || responseData.url || responseData.image_url || "";
      
      // Convert backend image path to accessible URL
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      if (imageUrl && !imageUrl.startsWith('http')) {
        const cleanPath = imageUrl.replace(/^\/+/, '').replace(/\\/g, '/');
        imageUrl = `${API_BASE_URL}/${cleanPath}`;
      }
      
      console.log('Modified Image URL:', imageUrl);
      
      // Update the generatedImageData as well
      const newImageData = [...generatedImageData];
      newImageData[imageIndex] = responseData;
      setGeneratedImageData(newImageData);
      
      setImages(images.map(img => 
        img.id === id ? { 
          ...img, 
          imageUrl: imageUrl, 
          isGenerating: false 
        } : img
      ));
      
      // Clear the input
      setUserInputs({ ...userInputs, [id]: "" });
      
      toast({
        title: "Image Modified",
        description: "New image has been generated based on your changes.",
      });
    } catch (error: any) {
      setImages(images.map(img => 
        img.id === id ? { ...img, isGenerating: false } : img
      ));
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          "Failed to modify image";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setModifyingImageId(null);
    }
  };

  const handleNext = () => {
    const approvedImages = images.filter(img => img.approved);
    if (approvedImages.length > 0) {
      // Pass both images and the full image data to Step4
      const approvedImageData = approvedImages.map(img => {
        const index = images.findIndex(i => i.id === img.id);
        return generatedImageData[index] || {
          scene: img.scene,
          image: img.imageUrl
        };
      });
      
      navigate("/step4", { 
        state: { 
          images: approvedImages,
          imageData: approvedImageData
        } 
      });
    } else {
      toast({
        title: "No Images Approved",
        description: "Please approve at least one image to continue.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-accent/5">
      <div className="container max-w-7xl mx-auto p-6 space-y-6 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Logo />
          <Button variant="ghost" onClick={() => navigate("/step2")}>
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
        </div>

        {/* Progress */}
        <StepProgress currentStep={3} steps={steps} />

        {/* Main Content */}
        <Card className="glass shadow-xl">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>AI Image Generation</CardTitle>
                <CardDescription>
                  {images.filter(img => img.approved).length} of {images.length} images approved
                </CardDescription>
              </div>
              <div className="flex gap-2">
                {images.length === 0 ? (
                  <Button onClick={handleGenerateAll} disabled={isGenerating} variant="gradient" size="lg">
                    {isGenerating ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <ImageIcon className="w-4 h-4" />
                        Generate All Images
                      </>
                    )}
                  </Button>
                ) : (
                  <Button onClick={handleNext} variant="gradient" size="lg">
                    Assemble Video
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {images.length === 0 ? (
              <div className="flex items-center justify-center h-64 text-muted-foreground">
                <div className="text-center space-y-2">
                  <ImageIcon className="w-12 h-12 mx-auto opacity-50" />
                  <p className="text-sm">Generate images from your approved prompts</p>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {images.map((image, index) => (
                  <Card key={image.id} className={`overflow-hidden transition-all ${image.approved ? 'border-primary shadow-lg ring-2 ring-primary/20' : ''}`}>
                    <div className="aspect-video relative bg-gradient-to-br from-primary/10 to-accent/10">
                      {image.isGenerating ? (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <Loader2 className="w-12 h-12 text-primary animate-spin" />
                        </div>
                      ) : image.imageUrl ? (
                        <>
                          <img 
                            src={image.imageUrl} 
                            alt={image.scene}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              // If image fails to load, show placeholder with path
                              const target = e.target as HTMLImageElement;
                              target.style.display = 'none';
                              const parent = target.parentElement;
                              if (parent) {
                                const errorDiv = document.createElement('div');
                                errorDiv.className = 'absolute inset-0 flex flex-col items-center justify-center p-4 text-xs text-muted-foreground text-center';
                                errorDiv.innerHTML = `
                                  <ImageIcon class="w-8 h-8 mb-2 opacity-50" />
                                  <p>Image generated but preview unavailable</p>
                                  <p class="mt-1 break-all">${image.imageUrl}</p>
                                `;
                                parent.appendChild(errorDiv);
                              }
                            }}
                          />
                        </>
                      ) : (
                        <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
                          <p className="text-sm">No image</p>
                        </div>
                      )}
                      {image.approved && (
                        <div className="absolute top-2 right-2">
                          <Badge variant="success">
                            <Check className="w-3 h-3" />
                            Approved
                          </Badge>
                        </div>
                      )}
                      <div className="absolute bottom-2 left-2">
                        <div className="w-8 h-8 bg-black/70 backdrop-blur-sm rounded-lg flex items-center justify-center text-sm font-bold text-white">
                          {index + 1}
                        </div>
                      </div>
                    </div>
                    <CardContent className="p-4 space-y-3">
                      <h3 className="font-semibold truncate">{image.scene}</h3>
                      
                      <div className="space-y-2">
                        <label className="text-xs font-medium text-muted-foreground">Request Changes:</label>
                        <Textarea
                          placeholder="e.g., 'Add more colors', 'Change background', 'Make it darker'..."
                          value={userInputs[image.id] || ""}
                          onChange={(e) => setUserInputs({ ...userInputs, [image.id]: e.target.value })}
                          className="min-h-[60px] text-sm"
                          disabled={image.isGenerating || modifyingImageId === image.id}
                        />
                      </div>
                      
                      <div className="flex gap-2">
                        <Button
                          onClick={() => handleApprove(image.id)}
                          variant={image.approved ? "outline" : "default"}
                          size="sm"
                          className="flex-1"
                          disabled={image.isGenerating}
                        >
                          <Check className="w-4 h-4" />
                          {image.approved ? "Approved" : "Approve"}
                        </Button>
                        <Button
                          onClick={() => handleModifyImage(image.id)}
                          variant="default"
                          size="sm"
                          disabled={image.isGenerating || modifyingImageId === image.id || !userInputs[image.id]?.trim()}
                          title="Modify with AI"
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          onClick={() => handleRegenerate(image.id)}
                          variant="outline"
                          size="sm"
                          disabled={image.isGenerating}
                          title="Regenerate"
                        >
                          <RefreshCw className="w-4 h-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
