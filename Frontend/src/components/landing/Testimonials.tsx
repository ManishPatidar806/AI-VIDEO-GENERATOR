import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Star, Quote } from "lucide-react";

const testimonials = [
  {
    id: 1,
    name: "Shreya Gupta",
    role: "Content Creator",
    avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop",
    rating: 5,
    text: "This platform has revolutionized my content creation workflow. I can now create professional videos in minutes instead of hours. The AI-generated visuals are stunning!",
  },
  {
    id: 2,
    name: "Rohit Shrivastav",
    role: "Marketing Director",
    avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop",
    rating: 5,
    text: "The automation is incredible. We've increased our video output by 300% while maintaining high quality. The AI storytelling feature is a game-changer for our marketing campaigns.",
  },
  {
    id: 3,
    name: "Isha Morgan",
    role: "Educator & YouTuber",
    avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop",
    rating: 5,
    text: "I love how easy it is to transform educational content into engaging videos. My students are more engaged, and I save countless hours on video editing. Highly recommend!",
  },
];

export const Testimonials = () => {
  return (
    <section className="py-20 md:py-32 relative overflow-hidden bg-muted/30">
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/5 rounded-full blur-3xl" />
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
            What Our{" "}
            <span className="bg-gradient-to-r from-primary via-accent to-[hsl(270,60%,65%)] bg-clip-text text-transparent">
              Users Say
            </span>
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground">
            Join thousands of creators who trust our platform
          </p>
        </motion.div>

        {/* Testimonials Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.id}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className="h-full border-2 hover:border-primary/50 transition-all duration-300 hover:shadow-2xl hover:shadow-primary/10 hover:-translate-y-2 relative overflow-hidden">
                {/* Quote Icon Background */}
                <div className="absolute top-0 right-0 w-32 h-32 opacity-5">
                  <Quote className="w-full h-full text-primary" />
                </div>

                <CardContent className="p-6 relative z-10">
                  {/* Rating */}
                  <div className="flex gap-1 mb-4">
                    {Array.from({ length: testimonial.rating }).map((_, i) => (
                      <Star
                        key={i}
                        className="w-5 h-5 fill-yellow-400 text-yellow-400"
                      />
                    ))}
                  </div>

                  {/* Testimonial Text */}
                  <p className="text-muted-foreground leading-relaxed mb-6 italic">
                    "{testimonial.text}"
                  </p>

                  {/* User Info */}
                  <div className="flex items-center gap-4">
                    <Avatar className="w-12 h-12 border-2 border-primary/20">
                      <AvatarImage
                        src={testimonial.avatar}
                        alt={testimonial.name}
                      />
                      <AvatarFallback className="bg-gradient-to-br from-primary to-accent text-white font-semibold">
                        {testimonial.name
                          .split(" ")
                          .map((n) => n[0])
                          .join("")}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="font-semibold">{testimonial.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {testimonial.role}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Trust Badge */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-16 flex flex-wrap items-center justify-center gap-4"
        >
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-background border border-border">
            <div className="flex -space-x-2">
              {testimonials.map((t) => (
                <Avatar key={t.id} className="w-8 h-8 border-2 border-background">
                  <AvatarImage src={t.avatar} alt={t.name} />
                  <AvatarFallback>{t.name.split(" ").map(n => n[0]).join("")}</AvatarFallback>
                </Avatar>
              ))}
            </div>
            <span className="text-sm font-medium">
              5,000+ happy creators
            </span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-background border border-border">
            <div className="flex gap-0.5">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
              ))}
            </div>
            <span className="text-sm font-medium">
              4.9/5 average rating
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  );
};
