import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api, authApi } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface User {
  id: string;
  email: string;
  name?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  // useEffect(() => {
  //   // Check for existing auth on mount
  //   const token = localStorage.getItem('auth_token');
  //   const storedUser = localStorage.getItem('user');
  //   if (token && storedUser) {
  //     try {
  //       setUser(JSON.parse(storedUser));
  //     } catch (e) {
  //       localStorage.removeItem('auth_token');
  //       localStorage.removeItem('user');
  //     }
  //   }
  //   setIsLoading(false);
  // }, []);


  useEffect(() => {
    refreshUser().finally(() => setIsLoading(false));
  }, []);


  const refreshUser = async () => {
    try {
      const response = await api.get('/api/v1/auth/me');
      setUser(response.data);
    } catch (err: any) {
      if (err.response?.status === 401) {
        try {
          await api.post('/api/v1/auth/refresh');
          const response = await api.get('/api/v1/auth/me');
          setUser(response.data);
        } catch {
          setUser(null);
        }
      } else {
        setUser(null);
      }
    }
  };


  const login = async (email: string, password: string) => {
    try {
      // const response = await authApi.login({ email, password });
      // const { token, user: userData } = response.data;
      // // localStorage.setItem('auth_token', token);
      // // localStorage.setItem('user', JSON.stringify(userData));
      // setUser(userData);
      const response = await api.post('/api/v1/auth/login', { email, password });
      setUser(response.data.user || { email });
      toast({
        title: 'Welcome back!',
        description: 'You have been logged in successfully.',
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Invalid credentials';

      if (typeof errorMessage === 'object') {
        // If it's an array of validation errors (like Zod), join the messages
        if (Array.isArray(errorMessage)) {
          error = errorMessage.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
        } else {
          error = JSON.stringify(error);
        }
      }
      toast({
        title: 'Login failed',
        description: error,
        variant: 'destructive',
      });
      throw error;
    }
  };

  const signup = async (email: string, password: string, name?: string) => {

    // const response = await authApi.signup({ email, password, name });
    // const { token, user: userData } = response.data;
    // localStorage.setItem('auth_token', token);
    // localStorage.setItem('user', JSON.stringify(userData));
    // setUser(userData);
    try {
      const response = await api.post('/api/v1/auth/signup', { email, password, name });
      setUser(response.data);
      toast({
        title: 'Account created!',
        description: 'Welcome to AI Video Creator.',
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Could not create account';
      toast({
        title: 'Signup failed',
        description: errorMessage,
        variant: 'destructive',
      });
      // throw error;
    }
  };

  // const logout = () => {
  //   localStorage.removeItem('auth_token');
  //   localStorage.removeItem('user');
  //   setUser(null);
  //   toast({
  //     title: 'Logged out',
  //     description: 'You have been logged out successfully.',
  //   });
  // };

  const logout = async () => {
    try {
      await api.post('/api/v1/auth/logout');
      setUser(null);
      toast({ title: 'Logged out', description: 'You have been logged out.' });
    } catch {
      setUser(null);
    }
  };


  return (
    <AuthContext.Provider value={{ user, isLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
