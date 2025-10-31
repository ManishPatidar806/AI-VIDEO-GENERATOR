import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft, Youtube, Loader2, CheckCircle2, XCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { pipelineApi } from "@/lib/api";

interface PipelineStatus {
  stage: string;
  progress: number;
  completed: boolean;
  error?: string;
}

export default function CompletePipeline() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState<PipelineStatus[]>([]);
  const [finalVideoUrl, setFinalVideoUrl] = useState<string>("");

  const stages = [
    "Extracting transcript",
    "Generating story",
    "Creating images",
    "Generating videos",
    "Creating voiceovers",
    "Assembling final video"
  ];

  const handleDownload = () => {
    if (finalVideoUrl) {
      // Create a temporary link to download the video
      const link = document.createElement('a');
      link.href = finalVideoUrl;
      link.download = 'ai-generated-video.mp4';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast({
        title: "Downloading",
        description: "Your video is being downloaded.",
      });
    }
  };

  const handleRunPipeline = async () => {
    if (!youtubeUrl) return;

    setIsRunning(true);
    setStatus([]);
    setFinalVideoUrl("");

    // Show progress stages as they happen
    const updateProgress = (stageIndex: number) => {
      setStatus(prev => {
        const newStatus = [...prev];
        newStatus[stageIndex] = {
          stage: stages[stageIndex],
          progress: ((stageIndex + 1) / stages.length) * 100,
          completed: true
        };
        return newStatus;
      });
    };

    // Initialize all stages as pending
    setStatus(stages.map(stage => ({
      stage,
      progress: 0,
      completed: false
    })));

    try {
      // Start the pipeline
      updateProgress(0); // Extracting transcript
      
      const response = await pipelineApi.runComplete({ youtube_url: youtubeUrl });
      
      // Check if the backend response indicates success
      if (response.data && !response.data.success) {
        throw new Error(response.data.message || "Pipeline failed");
      }
      
      // Mark remaining stages as complete after API success
      for (let i = 1; i < stages.length; i++) {
        updateProgress(i);
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      // Backend returns: { success, message, data: { final_video: "..." }, status_code }
      // Axios puts it in response.data, so we access response.data.data.final_video
      const responseData = response.data.data || response.data;
      let videoUrl = responseData.final_video || responseData.video_url || "";
      
      // Convert local path to accessible URL if needed
      if (videoUrl && !videoUrl.startsWith('http')) {
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        const cleanPath = videoUrl.replace(/^\/+/, '').replace(/\\/g, '/');
        videoUrl = `${API_BASE_URL}/${cleanPath}`;
      }
      
      setFinalVideoUrl(videoUrl);
      
      toast({
        title: "Pipeline Complete!",
        description: "Your video has been generated successfully.",
      });
    } catch (error: any) {
      const errorStage = status.findIndex(s => !s.completed);
      const stageName = errorStage >= 0 ? stages[errorStage] : "Final assembly";
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          "Pipeline failed";
      
      setStatus(prev => prev.map((s, i) => 
        i === errorStage ? { ...s, completed: false, error: errorMessage } : s
      ));
      
      toast({
        title: "Pipeline Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-accent/5">
      <div className="container max-w-4xl mx-auto p-6 space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <Logo />
          <Button variant="ghost" onClick={() => navigate("/")}>
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Button>
        </div>

        <Card className="glass shadow-xl">
          <CardHeader>
            <CardTitle>Complete Pipeline</CardTitle>
            <CardDescription>
              Run the full video generation pipeline from YouTube URL to final video
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Youtube className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  type="url"
                  placeholder="Paste YouTube URL here..."
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                  className="pl-10"
                  disabled={isRunning}
                />
              </div>
              <Button
                onClick={handleRunPipeline}
                disabled={!youtubeUrl || isRunning}
                variant="gradient"
              >
                {isRunning ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Running...
                  </>
                ) : (
                  "Run Pipeline"
                )}
              </Button>
            </div>

            {status.length > 0 && (
              <div className="space-y-4 animate-fade-in">
                <div className="space-y-3">
                  {status.map((s, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="flex items-center gap-2">
                          {s.completed && !s.error && (
                            <CheckCircle2 className="w-4 h-4 text-green-500" />
                          )}
                          {s.error && (
                            <XCircle className="w-4 h-4 text-destructive" />
                          )}
                          {!s.completed && !s.error && (
                            <Loader2 className="w-4 h-4 animate-spin text-primary" />
                          )}
                          {s.stage}
                        </span>
                        <span className="text-muted-foreground">
                          {s.completed && !s.error ? "Complete" : s.error ? "Failed" : "Processing..."}
                        </span>
                      </div>
                      <Progress value={s.progress} className="h-2" />
                      {s.error && (
                        <p className="text-sm text-destructive">{s.error}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {finalVideoUrl && (
              <div className="space-y-4 p-4 border rounded-lg bg-muted/50 animate-scale-in">
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircle2 className="w-5 h-5" />
                  <span className="font-semibold">Video Generated Successfully!</span>
                </div>
                <video
                  src={finalVideoUrl}
                  controls
                  className="w-full rounded-lg"
                />
                <div className="flex gap-2">
                  <Button onClick={handleDownload} className="flex-1" variant="gradient">
                    Download Video
                  </Button>
                  <Button onClick={() => navigate("/")} className="flex-1" variant="outline">
                    Create Another
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
