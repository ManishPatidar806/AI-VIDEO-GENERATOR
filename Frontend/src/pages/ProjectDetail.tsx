import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Download, Video, Image, FileText, Mic, RefreshCw } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [project, setProject] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading project data
    setTimeout(() => {
      setProject({
        id,
        title: "AI Tutorial Series - Episode 1",
        status: "completed",
        created_at: new Date().toISOString(),
        transcript: "This is a sample transcript...",
        story: [
          { id: "1", scene: "Opening", content: "Welcome to our AI tutorial..." },
          { id: "2", scene: "Introduction", content: "Today we'll explore..." },
        ],
        images: [
          { id: "1", url: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400", scene: "Opening" },
          { id: "2", url: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=600&h=400", scene: "Introduction" },
        ],
        videos: [
          { id: "1", url: "/mock-video.mp4", scene: "Opening" },
        ],
        voiceovers: [
          { id: "1", url: "/mock-audio.mp3", scene: "Opening" },
        ],
        final_video_url: "/mock-final-video.mp4",
      });
      setIsLoading(false);
    }, 1000);
  }, [id]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-accent/5 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-muted-foreground">Loading project...</p>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-accent/5 flex items-center justify-center">
        <Card className="glass p-8 text-center">
          <p className="text-muted-foreground">Project not found</p>
          <Button onClick={() => navigate("/projects")} className="mt-4">
            Back to Projects
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-accent/5">
      <div className="container max-w-6xl mx-auto p-6 space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <Logo />
          <Button variant="ghost" onClick={() => navigate("/projects")}>
            <ArrowLeft className="w-4 h-4" />
            Back to Projects
          </Button>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">{project.title}</h1>
            <p className="text-muted-foreground mt-1">
              Created {new Date(project.created_at).toLocaleDateString()}
            </p>
          </div>
          <Badge variant={project.status === "completed" ? "success" : "default"}>
            {project.status}
          </Badge>
        </div>

        {project.final_video_url && (
          <Card className="glass shadow-xl">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Video className="w-5 h-5" />
                  Final Video
                </CardTitle>
                <Button variant="gradient">
                  <Download className="w-4 h-4" />
                  Download
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <video
                src={project.final_video_url}
                controls
                className="w-full rounded-lg"
              />
            </CardContent>
          </Card>
        )}

        <Card className="glass shadow-xl">
          <CardContent className="p-6">
            <Tabs defaultValue="transcript" className="w-full">
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="transcript">
                  <FileText className="w-4 h-4 mr-2" />
                  Transcript
                </TabsTrigger>
                <TabsTrigger value="story">
                  <FileText className="w-4 h-4 mr-2" />
                  Story
                </TabsTrigger>
                <TabsTrigger value="images">
                  <Image className="w-4 h-4 mr-2" />
                  Images
                </TabsTrigger>
                <TabsTrigger value="videos">
                  <Video className="w-4 h-4 mr-2" />
                  Videos
                </TabsTrigger>
                <TabsTrigger value="voiceovers">
                  <Mic className="w-4 h-4 mr-2" />
                  Voiceovers
                </TabsTrigger>
              </TabsList>

              <TabsContent value="transcript" className="space-y-4 mt-4">
                <div className="p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm whitespace-pre-wrap">{project.transcript}</p>
                </div>
              </TabsContent>

              <TabsContent value="story" className="space-y-4 mt-4">
                {project.story?.map((scene: any) => (
                  <Card key={scene.id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-base">{scene.scene}</CardTitle>
                        <Button variant="ghost" size="sm">
                          <RefreshCw className="w-4 h-4" />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">{scene.content}</p>
                    </CardContent>
                  </Card>
                ))}
              </TabsContent>

              <TabsContent value="images" className="mt-4">
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {project.images?.map((image: any) => (
                    <Card key={image.id} className="overflow-hidden">
                      <img src={image.url} alt={image.scene} className="w-full aspect-video object-cover" />
                      <CardContent className="p-3">
                        <p className="text-sm font-medium">{image.scene}</p>
                        <Button variant="outline" size="sm" className="w-full mt-2">
                          <RefreshCw className="w-3 h-3" />
                          Regenerate
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="videos" className="mt-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {project.videos?.map((video: any) => (
                    <Card key={video.id}>
                      <CardContent className="p-4 space-y-2">
                        <p className="font-medium">{video.scene}</p>
                        <video src={video.url} controls className="w-full rounded" />
                        <Button variant="outline" size="sm" className="w-full">
                          <RefreshCw className="w-3 h-3" />
                          Regenerate
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="voiceovers" className="mt-4">
                <div className="space-y-3">
                  {project.voiceovers?.map((voiceover: any) => (
                    <Card key={voiceover.id}>
                      <CardContent className="p-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Mic className="w-5 h-5 text-primary" />
                          <div>
                            <p className="font-medium">{voiceover.scene}</p>
                            <audio src={voiceover.url} controls className="mt-2" />
                          </div>
                        </div>
                        <Button variant="outline" size="sm">
                          <RefreshCw className="w-4 h-4" />
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
