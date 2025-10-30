import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Logo } from "@/components/Logo";
import { StepProgress } from "@/components/StepProgress";
import { ProjectCard } from "@/components/ProjectCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Youtube, Sparkles, Image, Video, ArrowRight, Zap } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

const steps = [
  { number: 1, title: "Summarize" },
  { number: 2, title: "Prompts" },
  { number: 3, title: "Images" },
  { number: 4, title: "Video" },
];

const recentProjects = [
  { id: "1", title: "Travel Vlog Automation", status: "completed" as const },
  { id: "2", title: "Product Demo Video", status: "in-progress" as const },
  { id: "3", title: "Tutorial Series", status: "draft" as const },
];

export default function Home() {
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleStartCreation = () => {
    if (!user) {
      navigate("/auth");
      return;
    }
    if (youtubeUrl) {
      navigate("/step1", { state: { youtubeUrl } });
    }
  };

  const handleCompletePipeline = () => {
    if (!user) {
      navigate("/auth");
      return;
    }
    navigate("/pipeline");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-accent/5">
      <div className="container max-w-4xl mx-auto p-6 space-y-8 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Logo />
          <div className="flex gap-2">
            {user ? (
              <>
                <Button variant="ghost" onClick={() => navigate("/projects")}>
                  My Projects
                </Button>
                <Button variant="outline" onClick={logout}>
                  Logout
                </Button>
              </>
            ) : (
              <Button variant="gradient" onClick={() => navigate("/auth")}>
                Sign In
              </Button>
            )}
          </div>
        </div>

        {/* Hero Section */}
        <Card className="glass border-2 shadow-2xl animate-scale-in">
          <CardHeader className="text-center space-y-4">
            <div className="mx-auto w-16 h-16 bg-gradient-to-r from-primary via-accent to-[hsl(270,60%,65%)] rounded-2xl flex items-center justify-center shadow-xl animate-glow">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-3xl">Create AI-Powered Videos</CardTitle>
            <CardDescription className="text-base">
              Transform YouTube content into stunning AI-generated videos in 4 simple steps
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Step Progress */}
            <StepProgress currentStep={0} steps={steps} />

            {/* URL Input */}
            <div className="space-y-4">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Youtube className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    type="url"
                    placeholder="Paste YouTube URL here..."
                    value={youtubeUrl}
                    onChange={(e) => setYoutubeUrl(e.target.value)}
                    className="pl-10 h-12 text-base"
                  />
                </div>
                <Button
                  onClick={handleStartCreation}
                  disabled={!youtubeUrl}
                  variant="gradient"
                  size="lg"
                  className="px-8"
                >
                  Start Creating
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* Features Grid */}
            <div className="grid grid-cols-4 gap-4 pt-4">
              {[
                { icon: Youtube, label: "YouTube", color: "from-red-500 to-red-600" },
                { icon: Sparkles, label: "AI Summary", color: "from-primary to-accent" },
                { icon: Image, label: "Generate", color: "from-accent to-[hsl(270,60%,65%)]" },
                { icon: Video, label: "Assemble", color: "from-[hsl(270,60%,65%)] to-primary" },
              ].map((feature, index) => (
                <div
                  key={index}
                  className="flex flex-col items-center gap-2 p-4 rounded-xl glass hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
                >
                  <div className={`w-12 h-12 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center shadow-md`}>
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-xs font-medium text-center">{feature.label}</span>
                </div>
              ))}
            </div>

            {/* Quick Action */}
            <div className="pt-2">
              <Button 
                onClick={handleCompletePipeline}
                variant="outline"
                className="w-full"
              >
                <Zap className="w-4 h-4" />
                Complete Pipeline (One Click)
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Recent Projects */}
        {recentProjects.length > 0 && (
          <div className="space-y-4 animate-fade-in-up">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Recent Projects</h2>
              <Button variant="link" onClick={() => navigate("/projects")}>
                View All →
              </Button>
            </div>
            <div className="grid grid-cols-3 gap-4">
              {recentProjects.map((project) => (
                <ProjectCard
                  key={project.id}
                  {...project}
                  onOpen={() => navigate(`/project/${project.id}`)}
                  onDelete={() => console.log("Delete", project.id)}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
