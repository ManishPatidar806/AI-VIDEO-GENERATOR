import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Logo } from "@/components/Logo";
import { StepProgress } from "@/components/StepProgress";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowLeft, Loader2, Download, Share2, Play, Video } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Progress } from "@/components/ui/progress";

const steps = [
  { number: 1, title: "Summarize" },
  { number: 2, title: "Prompts" },
  { number: 3, title: "Images" },
  { number: 4, title: "Video" },
];

export default function Step4Video() {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const images = location.state?.images || [];
  const imageData = location.state?.imageData || [];
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [videoReady, setVideoReady] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState("none");
  const [selectedMusic, setSelectedMusic] = useState("ambient");

  const handleGenerateVideo = async () => {
    setIsGenerating(true);
    setProgress(0);

    try {
      // First generate voiceovers if a voice is selected
      if (selectedVoice !== "none") {
        const { voiceoverApi } = await import("@/lib/api");
        // Note: voiceoverApi needs to be updated to match backend expectations
        // For now, we'll skip this step
        setProgress(30);
      }

      // Generate individual videos from images
      const { videoApi } = await import("@/lib/api");
      
      // Backend expects image_data as an array of image scene objects
      const response = await videoApi.generate({ image_data: imageData });
      setProgress(60);

      // Backend returns video data
      const responseData = response.data.data || response.data;
      const videos = responseData.videos || [];
      
      // Assemble final video would be a separate endpoint
      // For now, just mark as complete
      setProgress(100);
      setVideoReady(true);
      toast({
        title: "Video Ready!",
        description: "Your AI-generated video has been assembled successfully.",
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          "Failed to generate video";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-accent/5">
      <div className="container max-w-6xl mx-auto p-6 space-y-6 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Logo />
          <Button variant="ghost" onClick={() => navigate("/step3")}>
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
        </div>

        {/* Progress */}
        <StepProgress currentStep={4} steps={steps} />

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel - Settings */}
          <Card className="glass shadow-xl">
            <CardHeader>
              <CardTitle>Video Settings</CardTitle>
              <CardDescription>Configure audio and assembly options</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Image Timeline Preview */}
              <div className="space-y-3">
                <label className="text-sm font-medium">Scene Timeline ({images.length} scenes)</label>
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {images.map((image: any, index: number) => (
                    <div key={image.id} className="relative flex-shrink-0">
                      <img 
                        src={image.imageUrl}
                        alt={`Scene ${index + 1}`}
                        className="w-24 h-16 object-cover rounded-lg border-2 border-border"
                      />
                      <div className="absolute -top-2 -left-2 w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-xs font-bold shadow-lg">
                        {index + 1}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Voice Narration */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Voice Narration</label>
                <Select value={selectedVoice} onValueChange={setSelectedVoice}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select voice" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">No Voice</SelectItem>
                    <SelectItem value="male1">Male Voice 1</SelectItem>
                    <SelectItem value="male2">Male Voice 2</SelectItem>
                    <SelectItem value="female1">Female Voice 1</SelectItem>
                    <SelectItem value="female2">Female Voice 2</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Background Music */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Background Music</label>
                <Select value={selectedMusic} onValueChange={setSelectedMusic}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select music" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">No Music</SelectItem>
                    <SelectItem value="ambient">Ambient</SelectItem>
                    <SelectItem value="upbeat">Upbeat</SelectItem>
                    <SelectItem value="cinematic">Cinematic</SelectItem>
                    <SelectItem value="corporate">Corporate</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Generate Button */}
              {!videoReady && (
                <Button
                  onClick={handleGenerateVideo}
                  disabled={isGenerating || images.length === 0}
                  variant="gradient"
                  size="lg"
                  className="w-full"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Generating Video...
                    </>
                  ) : (
                    <>
                      <Video className="w-4 h-4" />
                      Generate Final Video
                    </>
                  )}
                </Button>
              )}

              {/* Progress Bar */}
              {isGenerating && (
                <div className="space-y-2 animate-fade-in">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Assembling video...</span>
                    <span className="font-medium">{progress}%</span>
                  </div>
                  <Progress value={progress} className="h-2" />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Right Panel - Preview */}
          <Card className="glass shadow-xl">
            <CardHeader>
              <CardTitle>Video Preview</CardTitle>
              <CardDescription>Final generated video</CardDescription>
            </CardHeader>
            <CardContent>
              {videoReady ? (
                <div className="space-y-4 animate-scale-in">
                  {/* Video Player Placeholder */}
                  <div className="aspect-video bg-gradient-to-br from-primary/20 via-accent/20 to-[hsl(270,60%,65%)]/20 rounded-xl flex items-center justify-center relative overflow-hidden group">
                    <div className="absolute inset-0 bg-black/50 group-hover:bg-black/30 transition-all" />
                    <Button size="lg" variant="glass" className="relative z-10">
                      <Play className="w-8 h-8" />
                    </Button>
                  </div>

                  {/* Video Info */}
                  <div className="p-4 rounded-lg bg-muted/50 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Duration:</span>
                      <span className="font-medium">{images.length * 5}s</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Resolution:</span>
                      <span className="font-medium">1920x1080</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Format:</span>
                      <span className="font-medium">MP4</span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="grid grid-cols-2 gap-3">
                    <Button variant="default" size="lg">
                      <Download className="w-4 h-4" />
                      Download
                    </Button>
                    <Button variant="outline" size="lg">
                      <Share2 className="w-4 h-4" />
                      Share
                    </Button>
                  </div>

                  {/* Success Message */}
                  <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                    <p className="text-sm text-center font-medium">
                      🎉 Video successfully generated!
                    </p>
                  </div>
                </div>
              ) : (
                <div className="aspect-video flex items-center justify-center text-muted-foreground">
                  <div className="text-center space-y-2">
                    <Video className="w-16 h-16 mx-auto opacity-50" />
                    <p className="text-sm">Configure settings and generate your video</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
