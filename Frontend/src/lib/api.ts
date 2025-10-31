import axios,{ AxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, 
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
// api.interceptors.request.use(
//   (config) => {
//     const token = localStorage.getItem('auth_token');
//     if (token) {
//       config.headers.Authorization = `Bearer ${token}`;
//     }
//     return config;
//   },
//   (error) => Promise.reject(error)
// );



// Interceptor for handling expired access tokens
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Prevent infinite loop — don’t retry refresh itself
    if (originalRequest?.url?.includes('/auth/refresh')) {
      return Promise.reject(error);
    }

    // Handle access token expiration
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        console.log('🔄 Trying to refresh token...');
      } catch (refreshError) {
        console.warn('❌ Refresh failed — redirecting to login');
        window.location.href = '/auth';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);


// Utility function to extract video ID from YouTube URL
const extractYouTubeVideoId = (url: string): string => {
  try {
    const urlObj = new URL(url);
    
    // Handle different YouTube URL formats
    if (urlObj.hostname.includes('youtube.com')) {
      // Format: https://www.youtube.com/watch?v=VIDEO_ID
      const videoId = urlObj.searchParams.get('v');
      if (videoId) return videoId;
    } else if (urlObj.hostname.includes('youtu.be')) {
      // Format: https://youtu.be/VIDEO_ID
      const videoId = urlObj.pathname.slice(1).split('?')[0];
      if (videoId) return videoId;
    }
    
    // If it's already just an ID (no URL), return it as is
    if (!url.includes('://') && !url.includes('.')) {
      return url;
    }
    
    throw new Error('Invalid YouTube URL format');
  } catch (error) {
    throw new Error('Failed to extract video ID from URL');
  }
};

// Auth endpoints
export const authApi = {
  signup: (data: { email: string; password: string; name?: string }) =>
    api.post('/api/v1/auth/signup', data),
  login: (data: { email: string; password: string }) =>
    api.post('/api/v1/auth/login', data),
  logout: () =>
     api.post('/api/v1/auth/logout'), // optional logout endpoint
  me: () => 
    api.get('/api/v1/auth/me'), // fetch current logged-in user
};

// Transcript endpoints
export const transcriptApi = {
  generate: (data: { youtube_url: string }) => {
    const videoId = extractYouTubeVideoId(data.youtube_url);
    return api.post('/api/v1/generate/transcript', { videoId });
  },
};

// Story/Script endpoints
export const storyApi = {
  generate: (data: { summary: string }) =>
    api.post('/api/v1/generate/story', data),
  regenerate: (data: { summary: string; modifications?: string; existing_story?: any }) =>
    api.post('/api/v1/regenerate/story', data),
  regenerateScene: (data: { scene_indices: number[]; existing_story: any; summary: string }) =>
    api.post('/api/v1/regenerate/specific-scenes', data),
  updateScene: (data: { scene_id: string; content: string }) =>
    api.put('/api/v1/generate/update/scene', data),
  modifyScene: (data: { scene_data: any; user_input: string; summary?: string }) =>
    api.post('/api/v1/regenerate/modify-scene', data),
};

// Image endpoints
export const imageApi = {
  generate: (data: { story_data: any[]; output_dir?: string }) =>
    api.post('/api/v1/generate/images', data),
  regenerate: (data: { scene_data: any; output_dir?: string }) =>
    api.post('/api/v1/regenerate/image', data),
  batchRegenerate: (data: { story_data: any[]; output_dir?: string }) =>
    api.post('/api/v1/regenerate/batch-regenerate/images', data),
  modifyImage: (data: { scene_data: any; user_input: string; output_dir?: string }) =>
    api.post('/api/v1/regenerate/modify-image', data),
};

// Video endpoints
export const videoApi = {
  generate: (data: { image_data: any[]; output_dir?: string }) =>
    api.post('/api/v1/generate/videos', data),
  regenerate: (data: { image_scene_data: any; output_dir?: string }) =>
    api.post('/api/v1/regenerate/video', data),
  batchRegenerate: (data: { image_data: any[]; output_dir?: string }) =>
    api.post('/api/v1/regenerate/batch-regenerate/videos', data),
};

// Voiceover endpoints
export const voiceoverApi = {
  generate: (data: { story_id: string; voice_id?: string }) =>
    api.post('/api/v1/generate/voiceovers', data),
  regenerate: (data: { voiceover_id: string; voice_id?: string }) =>
    api.post('/api/v1/regenerate/voiceover', data),
};

// Final assembly endpoints
export const finalVideoApi = {
  generate: (data: { 
    project_id: string;
    video_ids: string[];
    voiceover_ids?: string[];
    music_url?: string;
  }) =>
    api.post('/api/v1/generate/final-video', data),
};

// Complete pipeline endpoint
export const pipelineApi = {
  runComplete: (data: { youtube_url: string; voice_id?: string }) => {
    const videoId = extractYouTubeVideoId(data.youtube_url);
    return api.post('/api/v1/generate/complete-pipeline', { 
      videoId,
      output_video_name: 'final_ai_video.mp4'
    });
  },
  regenerateScenes: (data: { project_id: string; scene_ids: string[] }) =>
    api.post('/api/v1/regenerate/specific-scenes', data),
};
