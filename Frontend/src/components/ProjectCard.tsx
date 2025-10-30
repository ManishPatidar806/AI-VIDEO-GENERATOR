import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Trash2, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";

interface ProjectCardProps {
  id: string;
  title: string;
  thumbnail?: string;
  status: "completed" | "in-progress" | "draft";
  onOpen: () => void;
  onDelete: () => void;
}

export const ProjectCard = ({ title, thumbnail, status, onOpen, onDelete }: ProjectCardProps) => {
  const statusConfig = {
    completed: { variant: "success" as const, label: "Completed" },
    "in-progress": { variant: "info" as const, label: "In Progress" },
    draft: { variant: "default" as const, label: "Draft" }
  };

  return (
    <Card className="group hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
      <div className="aspect-video bg-gradient-to-br from-primary/10 via-accent/10 to-[hsl(270,60%,65%)]/10 relative overflow-hidden">
        {thumbnail ? (
          <img src={thumbnail} alt={title} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-6xl font-bold text-muted-foreground/20">AI</div>
          </div>
        )}
        <div className="absolute top-2 right-2">
          <Badge variant={statusConfig[status].variant}>
            {statusConfig[status].label}
          </Badge>
        </div>
      </div>
      <CardContent className="p-4">
        <h3 className="font-semibold text-lg truncate">{title}</h3>
      </CardContent>
      <CardFooter className="p-4 pt-0 gap-2">
        <Button onClick={onOpen} className="flex-1" size="sm">
          <ExternalLink className="w-4 h-4" />
          Open
        </Button>
        <Button onClick={onDelete} variant="outline" size="sm">
          <Trash2 className="w-4 h-4" />
        </Button>
      </CardFooter>
    </Card>
  );
};
