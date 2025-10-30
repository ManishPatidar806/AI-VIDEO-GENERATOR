import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Logo } from "@/components/Logo";
import { StepProgress } from "@/components/StepProgress";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ArrowRight, ArrowLeft, Loader2, Youtube, Sparkles } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const steps = [
  { number: 1, title: "Summarize" },
  { number: 2, title: "Prompts" },
  { number: 3, title: "Images" },
  { number: 4, title: "Video" },
];

export default function Step1Summarize() {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [summary, setSummary] = useState("");
  const youtubeUrl = location.state?.youtubeUrl || "";

  const handleGenerateSummary = async () => {
    setIsLoading(true);
    try {
      const { transcriptApi } = await import("@/lib/api");
      const response = await transcriptApi.generate({ youtube_url: youtubeUrl });
      
      // Backend returns: { success, message, data: { summary: "..." }, status_code }
      // Axios puts it in response.data, so we access response.data.data.summary
      const summaryText = response.data.data?.summary || response.data.summary || "";
      
      if (!summaryText) {
        throw new Error("No summary returned from the server");
      }
      
      setSummary(summaryText);
      toast({
        title: "Summary Generated",
        description: "YouTube video has been successfully summarized.",
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          "Failed to generate summary";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerateSummary = async () => {
    setIsLoading(true);
    try {
      const { transcriptApi } = await import("@/lib/api");
      const response = await transcriptApi.generate({ youtube_url: youtubeUrl });
      
      // Backend returns: { success, message, data: { summary: "..." }, status_code }
      // Axios puts it in response.data, so we access response.data.data.summary
      const summaryText = response.data.data?.summary || response.data.summary || "";
      
      if (!summaryText) {
        throw new Error("No summary returned from the server");
      }
      
      setSummary(summaryText);
      toast({
        title: "Summary Regenerated",
        description: "A new summary has been generated.",
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          "Failed to regenerate summary";
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
    if (summary) {
      navigate("/step2", { state: { summary, youtubeUrl } });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-accent/5">
      <div className="container max-w-5xl mx-auto p-6 space-y-6 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Logo />
          <Button variant="ghost" onClick={() => navigate("/")}>
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Button>
        </div>

        {/* Progress */}
        <StepProgress currentStep={1} steps={steps} />

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel - Input */}
          <Card className="glass shadow-xl">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg">
                  <Youtube className="w-6 h-6 text-white" />
                </div>
                <div>
                  <CardTitle>Step 1: Summarize Video</CardTitle>
                  <CardDescription>Extract and analyze YouTube content</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 rounded-lg bg-muted/50 border">
                <p className="text-sm font-medium text-muted-foreground mb-1">YouTube URL:</p>
                <p className="text-sm truncate">{youtubeUrl || "No URL provided"}</p>
              </div>

              <Button
                onClick={handleGenerateSummary}
                disabled={isLoading || !youtubeUrl}
                variant="gradient"
                className="w-full"
                size="lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Generating Summary...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Summary
                  </>
                )}
              </Button>

              {summary && (
                <div className="pt-4 space-y-3 animate-fade-in">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    Summary generated successfully
                  </div>
                  <Button onClick={handleNext} className="w-full" size="lg">
                    Continue to Prompt Generation
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Right Panel - Output */}
          <Card className="glass shadow-xl">
            <CardHeader>
              <CardTitle>Generated Summary</CardTitle>
              <CardDescription>AI-extracted content overview</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex flex-col items-center justify-center h-64 space-y-4">
                  <Loader2 className="w-12 h-12 text-primary animate-spin" />
                  <p className="text-sm text-muted-foreground">Analyzing video content...</p>
                </div>
              ) : summary ? (
                <div className="space-y-4 animate-scale-in">
                  <Textarea
                    value={summary}
                    onChange={(e) => setSummary(e.target.value)}
                    className="min-h-[300px] resize-none"
                    placeholder="Summary will appear here..."
                  />
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      Edit Summary
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="flex-1"
                      onClick={handleRegenerateSummary}
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-3 h-3 animate-spin" />
                          Regenerating...
                        </>
                      ) : (
                        "Regenerate"
                      )}
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-64 text-muted-foreground">
                  <div className="text-center space-y-2">
                    <Sparkles className="w-12 h-12 mx-auto opacity-50" />
                    <p className="text-sm">Click "Generate Summary" to begin</p>
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
