import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Logo } from "@/components/Logo";
import { StepProgress } from "@/components/StepProgress";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, ArrowLeft, Loader2, Check, RefreshCw, Sparkles } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";

const steps = [
  { number: 1, title: "Summarize" },
  { number: 2, title: "Prompts" },
  { number: 3, title: "Images" },
  { number: 4, title: "Video" },
];

interface Prompt {
  id: string;
  scene: string;
  description: string;
}

export default function Step2Prompts() {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [storyData, setStoryData] = useState<any>(null);
  const summary = location.state?.summary || "";

  const handleGeneratePrompts = async () => {
    setIsLoading(true);
    try {
      const { storyApi } = await import("@/lib/api");
      // Backend expects summary, not transcript_id
      const response = await storyApi.generate({ summary });
      
      // Backend returns: { success, message, data: { scenes: [...], ... }, status_code }
      // Axios puts it in response.data, so we access response.data.data.scenes
      const storyDataResponse = response.data.data || response.data;
      const scenes = storyDataResponse.scenes || [];
      
      // Store the full story data for later use
      setStoryData(storyDataResponse);
      
      const generatedPrompts = scenes.map((scene: any, index: number) => ({
        id: scene.id || `${index + 1}`,
        scene: scene.title || scene.scene,
        description: scene.description || scene.prompt || scene.visual_cues,
      }));
      
      setPrompts(generatedPrompts);
      toast({
        title: "Prompts Generated",
        description: "Scene prompts have been created from the summary.",
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          "Failed to generate prompts";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = (id: string) => {
    // Removed: No longer needed
  };

  const handleRegenerate = async (id: string) => {
    setIsLoading(true);
    try {
      const { storyApi } = await import("@/lib/api");
      
      // Find the index of the scene to regenerate
      const sceneIndex = prompts.findIndex(p => p.id === id);
      
      if (sceneIndex === -1 || !storyData) {
        throw new Error("Scene not found");
      }
      
      // Call the regenerate specific scene endpoint
      const response = await storyApi.regenerateScene({ 
        scene_indices: [sceneIndex],
        existing_story: storyData,
        summary: summary
      });
      
      // Update the story data and prompts
      const storyDataResponse = response.data.data || response.data;
      const scenes = storyDataResponse.scenes || [];
      setStoryData(storyDataResponse);
      
      const generatedPrompts = scenes.map((scene: any, index: number) => ({
        id: scene.id || `${index + 1}`,
        scene: scene.title || scene.scene,
        description: scene.description || scene.prompt || scene.visual_cues,
      }));
      
      setPrompts(generatedPrompts);
      
      toast({
        title: "Scene Regenerated",
        description: `Scene ${sceneIndex + 1} has been regenerated successfully.`,
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          "Failed to regenerate scene";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleNext = () => {
    if (prompts.length > 0) {
      // Pass both prompts and the full story data to Step3
      navigate("/step3", { 
        state: { 
          prompts: prompts,
          storyData: storyData
        } 
      });
    } else {
      toast({
        title: "No Prompts Generated",
        description: "Please generate prompts first.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-accent/5">
      <div className="container max-w-6xl mx-auto p-6 space-y-6 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Logo />
          <Button variant="ghost" onClick={() => navigate("/step1")}>
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
        </div>

        {/* Progress */}
        <StepProgress currentStep={2} steps={steps} />

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - Summary */}
          <Card className="glass shadow-xl lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-lg">Summary</CardTitle>
              <CardDescription>Source content</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="prose prose-sm max-h-[400px] overflow-y-auto text-sm text-muted-foreground">
                {summary || "No summary available"}
              </div>
              <Button
                onClick={handleGeneratePrompts}
                disabled={isLoading || prompts.length > 0}
                variant="gradient"
                className="w-full mt-4"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Prompts
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Right Panel - Prompts */}
          <Card className="glass shadow-xl lg:col-span-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Scene Prompts</CardTitle>
                  <CardDescription>
                    {prompts.length} scenes generated
                  </CardDescription>
                </div>
                {prompts.length > 0 && (
                  <Button onClick={handleNext} variant="gradient">
                    Continue to Images
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {prompts.length === 0 ? (
                <div className="flex items-center justify-center h-64 text-muted-foreground">
                  <div className="text-center space-y-2">
                    <Sparkles className="w-12 h-12 mx-auto opacity-50" />
                    <p className="text-sm">Generate prompts to continue</p>
                  </div>
                </div>
              ) : (
                prompts.map((prompt, index) => (
                  <Collapsible key={prompt.id} defaultOpen={index === 0}>
                    <Card className="transition-all">
                      <CollapsibleTrigger className="w-full">
                        <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center text-sm font-bold text-white">
                                {index + 1}
                              </div>
                              <div className="text-left">
                                <CardTitle className="text-base">{prompt.scene}</CardTitle>
                              </div>
                            </div>
                          </div>
                        </CardHeader>
                      </CollapsibleTrigger>
                      <CollapsibleContent>
                        <CardContent className="space-y-3">
                          <p className="text-sm text-muted-foreground">{prompt.description}</p>
                          <div className="flex gap-2">
                            <Button
                              onClick={() => handleRegenerate(prompt.id)}
                              variant="outline"
                              size="sm"
                              disabled={isLoading}
                              className="w-full"
                            >
                              {isLoading ? (
                                <>
                                  <Loader2 className="w-4 h-4 animate-spin" />
                                  Regenerating...
                                </>
                              ) : (
                                <>
                                  <RefreshCw className="w-4 h-4" />
                                  Regenerate Scene
                                </>
                              )}
                            </Button>
                          </div>
                        </CardContent>
                      </CollapsibleContent>
                    </Card>
                  </Collapsible>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
