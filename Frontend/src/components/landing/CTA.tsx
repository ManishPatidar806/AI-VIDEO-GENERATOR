import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

export const CTA = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleSignUp = () => {
    if (user) {
      navigate("/pipeline");
    } else {
      navigate("/auth?mode=signup");
    }
  };

  const handleLogin = () => {
    navigate("/auth?mode=login");
  };

  return (
    <section className="py-20 md:py-32 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-accent/10 to-[hsl(270,60%,65%)]/10">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 90, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear",
          }}
          className="absolute top-0 left-0 w-full h-full opacity-20"
          style={{
            backgroundImage: `radial-gradient(circle at 50% 50%, hsl(var(--primary)) 1px, transparent 1px)`,
            backgroundSize: "50px 50px",
          }}
        />
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto"
        >
          {/* Glass Card */}
          <div className="relative rounded-3xl bg-background/80 backdrop-blur-xl border-2 border-primary/20 shadow-2xl overflow-hidden">
            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5" />
            
            {/* Glow Effect */}
            <div className="absolute -inset-1 bg-gradient-to-r from-primary via-accent to-[hsl(270,60%,65%)] opacity-20 blur-xl" />

            <div className="relative z-10 p-8 md:p-12 lg:p-16 text-center space-y-8">
              {/* Icon */}
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                whileInView={{ scale: 1, rotate: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="mx-auto w-20 h-20 rounded-2xl bg-gradient-to-br from-primary via-accent to-[hsl(270,60%,65%)] flex items-center justify-center shadow-2xl"
              >
                <Sparkles className="w-10 h-10 text-white" />
              </motion.div>

              {/* Heading */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold mb-4">
                  Start Creating{" "}
                  <span className="bg-gradient-to-r from-primary via-accent to-[hsl(270,60%,65%)] bg-clip-text text-transparent">
                    AI Videos
                  </span>{" "}
                  Today!
                </h2>
                <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
                  Join thousands of creators transforming YouTube content into
                  professional videos with the power of AI
                </p>
              </motion.div>

              {/* Buttons */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="flex flex-col sm:flex-row items-center justify-center gap-4"
              >
                {user ? (
                  <Button
                    size="lg"
                    onClick={handleSignUp}
                    className="w-full sm:w-auto text-lg px-10 py-7 bg-gradient-to-r from-primary via-accent to-[hsl(270,60%,65%)] text-white font-semibold shadow-2xl hover:shadow-primary/50 transition-all duration-300 hover:scale-105"
                  >
                    Create Your Video
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Button>
                ) : (
                  <>
                    <Button
                      size="lg"
                      onClick={handleSignUp}
                      className="w-full sm:w-auto text-lg px-10 py-7 bg-gradient-to-r from-primary via-accent to-[hsl(270,60%,65%)] text-white font-semibold shadow-2xl hover:shadow-primary/50 transition-all duration-300 hover:scale-105"
                    >
                      Sign Up Free
                      <ArrowRight className="ml-2 w-5 h-5" />
                    </Button>
                    <Button
                      size="lg"
                      variant="outline"
                      onClick={handleLogin}
                      className="w-full sm:w-auto text-lg px-10 py-7 font-semibold border-2 hover:bg-muted/50 transition-all duration-300"
                    >
                      Login
                    </Button>
                  </>
                )}
              </motion.div>

              {/* Features List */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.5 }}
                className="flex flex-wrap items-center justify-center gap-6 pt-4 text-sm"
              >
                {[
                  "✓ No credit card required",
                  "✓ 5-minute setup",
                  "✓ Cancel anytime",
                ].map((feature, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.8 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.3, delay: 0.6 + index * 0.1 }}
                    className="flex items-center gap-2 text-muted-foreground"
                  >
                    <span className="font-medium">{feature}</span>
                  </motion.div>
                ))}
              </motion.div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};
