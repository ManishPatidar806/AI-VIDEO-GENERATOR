import { motion } from "framer-motion";
import { Link, Sparkles, Image, Video, Download, ArrowRight } from "lucide-react";

const steps = [
  {
    number: 1,
    icon: Link,
    title: "Input YouTube URL",
    description: "Paste any YouTube video link to get started with the AI processing pipeline.",
    color: "from-blue-500 to-cyan-500",
  },
  {
    number: 2,
    icon: Sparkles,
    title: "Generate Summary",
    description: "AI analyzes and creates a comprehensive summary of the video content.",
    color: "from-purple-500 to-pink-500",
  },
  {
    number: 3,
    icon: Sparkles,
    title: "Create Story",
    description: "Transform the summary into an engaging narrative with AI storytelling.",
    color: "from-orange-500 to-red-500",
  },
  {
    number: 4,
    icon: Image,
    title: "Generate Images",
    description: "AI creates stunning visuals that complement your story perfectly.",
    color: "from-green-500 to-emerald-500",
  },
  {
    number: 5,
    icon: Download,
    title: "Export Final Video",
    description: "Download your professional AI-generated video ready to share anywhere.",
    color: "from-indigo-500 to-purple-500",
  },
];

export const HowItWorks = () => {
  return (
    <section id="how-it-works" className="py-20 md:py-32 relative overflow-hidden bg-muted/30">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, hsl(var(--primary)) 1px, transparent 0)`,
          backgroundSize: '40px 40px'
        }} />
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-3xl mx-auto mb-16"
        >
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
            How It{" "}
            <span className="bg-gradient-to-r from-primary via-accent to-[hsl(270,60%,65%)] bg-clip-text text-transparent">
              Works
            </span>
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground">
            Create professional videos in 5 simple steps
          </p>
        </motion.div>

        {/* Steps - Desktop View */}
        <div className="hidden lg:block">
          <div className="relative">
            {/* Connection Line */}
            <div className="absolute top-24 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500 opacity-20" />
            
            <div className="grid grid-cols-5 gap-8">
              {steps.map((step, index) => {
                const Icon = step.icon;
                return (
                  <motion.div
                    key={step.number}
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-100px" }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className="relative"
                  >
                    {/* Step Number Badge */}
                    <motion.div
                      whileHover={{ scale: 1.1 }}
                      className={`w-20 h-20 mx-auto rounded-full bg-gradient-to-br ${step.color} flex items-center justify-center shadow-2xl mb-6 relative z-10`}
                    >
                      <span className="text-2xl font-bold text-white">
                        {step.number}
                      </span>
                    </motion.div>

                    {/* Icon */}
                    <motion.div
                      whileHover={{ rotate: 360 }}
                      transition={{ duration: 0.6 }}
                      className="w-12 h-12 mx-auto mb-4 rounded-xl bg-card border-2 border-primary/20 flex items-center justify-center"
                    >
                      <Icon className="w-6 h-6 text-primary" />
                    </motion.div>

                    {/* Content */}
                    <div className="text-center">
                      <h3 className="text-lg font-bold mb-2">{step.title}</h3>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {step.description}
                      </p>
                    </div>

                    {/* Arrow */}
                    {index < steps.length - 1 && (
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.5, delay: index * 0.1 + 0.3 }}
                        className="absolute top-10 -right-4 z-0"
                      >
                        <ArrowRight className="w-8 h-8 text-primary/30" />
                      </motion.div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Steps - Mobile/Tablet View */}
        <div className="lg:hidden space-y-8">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <motion.div
                key={step.number}
                initial={{ opacity: 0, x: -50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="flex gap-6 items-start"
              >
                {/* Left Side - Number & Icon */}
                <div className="flex-shrink-0">
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    className={`w-16 h-16 rounded-full bg-gradient-to-br ${step.color} flex items-center justify-center shadow-xl mb-3`}
                  >
                    <span className="text-xl font-bold text-white">
                      {step.number}
                    </span>
                  </motion.div>
                  <div className="w-16 h-12 flex items-center justify-center">
                    <Icon className="w-6 h-6 text-primary" />
                  </div>
                </div>

                {/* Right Side - Content */}
                <div className="flex-1 pt-2">
                  <h3 className="text-xl font-bold mb-2">{step.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mt-16 text-center"
        >
          <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-to-r from-primary/10 via-accent/10 to-[hsl(270,60%,65%)]/10 border border-primary/20">
            <Video className="w-5 h-5 text-primary" />
            <span className="text-sm md:text-base font-medium">
              From URL to video in under 5 minutes
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  );
};
