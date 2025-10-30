import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Logo } from "@/components/Logo";
import { ProjectCard } from "@/components/ProjectCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Plus, Search, ArrowLeft } from "lucide-react";

const mockProjects = [
  { id: "1", title: "AI Tutorial Series - Episode 1", status: "completed" as const, thumbnail: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=300&fit=crop" },
  { id: "2", title: "Product Demo Video", status: "in-progress" as const, thumbnail: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=400&h=300&fit=crop" },
  { id: "3", title: "Travel Vlog Automation", status: "completed" as const, thumbnail: "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=400&h=300&fit=crop" },
  { id: "4", title: "Educational Content", status: "draft" as const },
  { id: "5", title: "Marketing Campaign Video", status: "in-progress" as const, thumbnail: "https://images.unsplash.com/photo-1551434678-e076c223a692?w=400&h=300&fit=crop" },
  { id: "6", title: "Social Media Shorts", status: "completed" as const, thumbnail: "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400&h=300&fit=crop" },
];

export default function Projects() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [projects, setProjects] = useState(mockProjects);

  const filteredProjects = projects.filter(project =>
    project.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDelete = (id: string) => {
    setProjects(projects.filter(p => p.id !== id));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-accent/5">
      <div className="container max-w-7xl mx-auto p-6 space-y-6 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Logo />
          <Button variant="ghost" onClick={() => navigate("/")}>
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Button>
        </div>

        {/* Title & Actions */}
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">My Projects</h1>
            <p className="text-muted-foreground mt-1">{projects.length} total projects</p>
          </div>
          <Button onClick={() => navigate("/")} variant="gradient" size="lg">
            <Plus className="w-4 h-4" />
            New Project
          </Button>
        </div>

        {/* Search */}
        <Card className="glass p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </Card>

        {/* Projects Grid */}
        {filteredProjects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in-up">
            {filteredProjects.map((project) => (
              <ProjectCard
                key={project.id}
                {...project}
                onOpen={() => navigate(`/project/${project.id}`)}
                onDelete={() => handleDelete(project.id)}
              />
            ))}
          </div>
        ) : (
          <Card className="glass p-12">
            <div className="text-center text-muted-foreground">
              <Search className="w-16 h-16 mx-auto opacity-50 mb-4" />
              <p>No projects found matching "{searchQuery}"</p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
