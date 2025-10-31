import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { PlayCircle, ArrowRight, Clock, Eye } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

const demoVideos = [
  {
    id: 1,
    title: "Tech Review: Latest AI Innovations",
    thumbnail: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=450&fit=crop",
    duration: "3:45",
    views: "12.5K",
  },
  {
    id: 2,
    title: "Travel Vlog: Exploring New Horizons",
    thumbnail: "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&h=450&fit=crop",
    duration: "2:30",
    views: "8.2K",
  },
  {
    id: 3,
    title: "Tutorial: Mastering Digital Skills",
    thumbnail: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&h=450&fit=crop",
    duration: "4:15",
    views: "15.8K",
  },
];

export const Demo = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleGenerateOwn = () => {
    if (user) {
      navigate("/pipeline");
    } else {
      navigate("/auth?mode=signup");
    }
  };

  return (
    <section id="demo" className="py-20 md:py-32 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-accent/5 to-transparent" />

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
            See{" "}
            <span className="bg-gradient-to-r from-primary via-accent to-[hsl(270,60%,65%)] bg-clip-text text-transparent">
              AI in Action
            </span>
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground">
            Explore sample videos created by our AI-powered platform
          </p>
        </motion.div>

        {/* Featured Video */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto mb-12"
        >
          <Card className="overflow-hidden border-2 hover:border-primary/50 transition-all duration-300 shadow-2xl group">
            <div className="relative aspect-video bg-gradient-to-br from-primary/20 via-accent/20 to-[hsl(270,60%,65%)]/20">
              {/* Video Thumbnail */}
              <img
                src="https://images.unsplash.com/photo-1611162616475-46b635cb6868?w=1200&h=675&fit=crop"
                alt="Featured AI-generated video"
                className="w-full h-full object-cover"
              />
              
              {/* Play Overlay */}
              <motion.div
                whileHover={{ scale: 1.1 }}
                className="absolute inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center cursor-pointer group-hover:bg-black/50 transition-all"
              >
                <motion.div
                  whileHover={{ scale: 1.2 }}
                  className="w-20 h-20 rounded-full bg-white/90 flex items-center justify-center shadow-2xl"
                >
                  <PlayCircle className="w-12 h-12 text-primary" />
                </motion.div>
              </motion.div>

              {/* Video Info Badge */}
              <div className="absolute top-4 right-4 flex gap-2">
                <div className="px-3 py-1.5 rounded-full bg-black/70 backdrop-blur-sm text-white text-sm font-medium flex items-center gap-1.5">
                  <Clock className="w-4 h-4" />
                  5:30
                </div>
                <div className="px-3 py-1.5 rounded-full bg-black/70 backdrop-blur-sm text-white text-sm font-medium flex items-center gap-1.5">
                  <Eye className="w-4 h-4" />
                  25.4K
                </div>
              </div>
            </div>
            <CardContent className="p-6">
              <h3 className="text-2xl font-bold mb-2">
                Featured: AI-Generated Documentary
              </h3>
              <p className="text-muted-foreground">
                Watch this stunning example of what our AI can create from a simple YouTube URL
              </p>
            </CardContent>
          </Card>
        </motion.div>

        {/* More Examples Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {demoVideos.map((video, index) => (
            <motion.div
              key={video.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className="overflow-hidden border hover:border-primary/50 transition-all duration-300 hover:shadow-xl group cursor-pointer">
                <div className="relative aspect-video bg-muted">
                  <img
                    src={video.thumbnail}
                    alt={video.title}
                    className="w-full h-full object-cover"
                  />
                  
                  {/* Play Overlay */}
                  <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <motion.div
                      whileHover={{ scale: 1.1 }}
                      className="w-14 h-14 rounded-full bg-white/90 flex items-center justify-center"
                    >
                      <PlayCircle className="w-8 h-8 text-primary" />
                    </motion.div>
                  </div>

                  {/* Duration Badge */}
                  <div className="absolute bottom-2 right-2 px-2 py-1 rounded bg-black/70 backdrop-blur-sm text-white text-xs font-medium">
                    {video.duration}
                  </div>
                </div>
                <CardContent className="p-4">
                  <h4 className="font-semibold mb-1 line-clamp-2">
                    {video.title}
                  </h4>
                  <p className="text-sm text-muted-foreground flex items-center gap-1">
                    <Eye className="w-3.5 h-3.5" />
                    {video.views} views
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* CTA Button */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="text-center"
        >
          <Button
            size="lg"
            onClick={handleGenerateOwn}
            className="text-lg px-8 py-6 bg-gradient-to-r from-primary via-accent to-[hsl(270,60%,65%)] text-white font-semibold shadow-2xl hover:shadow-primary/50 transition-all duration-300 hover:scale-105"
          >
            Generate Your Own Video
            <ArrowRight className="ml-2 w-5 h-5" />
          </Button>
        </motion.div>
      </div>
    </section>
  );
};
