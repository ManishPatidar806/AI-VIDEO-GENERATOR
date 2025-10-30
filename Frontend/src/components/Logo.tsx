import { Sparkles } from "lucide-react";

export const Logo = () => {
  return (
    <div className="flex items-center gap-2">
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-primary via-accent to-[hsl(270,60%,65%)] blur-lg opacity-50 rounded-full" />
        <div className="relative w-10 h-10 bg-gradient-to-r from-primary via-accent to-[hsl(270,60%,65%)] rounded-xl flex items-center justify-center shadow-xl">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
      </div>
      <div>
        <h1 className="text-xl font-bold gradient-text">AI Video Creator</h1>
        <p className="text-xs text-muted-foreground">Generative Video System</p>
      </div>
    </div>
  );
};
