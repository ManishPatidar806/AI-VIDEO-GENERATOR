import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import LandingPage from "./pages/LandingPage";
import Home from "./pages/Home";
import Step1Summarize from "./pages/Step1Summarize";
import Step2Prompts from "./pages/Step2Prompts";
import Step3Images from "./pages/Step3Images";
import Step4Video from "./pages/Step4Video";
import Projects from "./pages/Projects";
import Auth from "./pages/Auth";
import CompletePipeline from "./pages/CompletePipeline";
import ProjectDetail from "./pages/ProjectDetail";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={<ProtectedRoute><Home /></ProtectedRoute>} />
            <Route path="/auth" element={<Auth />} />
            <Route 
              path="/step1" 
              element={
                <ProtectedRoute>
                  <Step1Summarize />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/step2" 
              element={
                <ProtectedRoute>
                  <Step2Prompts />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/step3" 
              element={
                <ProtectedRoute>
                  <Step3Images />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/step4" 
              element={
                <ProtectedRoute>
                  <Step4Video />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/projects" 
              element={
                <ProtectedRoute>
                  <Projects />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/project/:id" 
              element={
                <ProtectedRoute>
                  <ProjectDetail />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/pipeline" 
              element={
                <ProtectedRoute>
                  <CompletePipeline />
                </ProtectedRoute>
              } 
            />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
