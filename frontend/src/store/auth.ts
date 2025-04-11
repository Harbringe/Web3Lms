import { create } from 'zustand';
import { mountStoreDevtool } from 'simple-zustand-devtools';

interface User {
  user_id: string;
  email: string;
  full_name: string;
  token?: string;
}

interface AuthState {
  user: User | null;
  loading: boolean;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  isLoggedIn: () => boolean;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  loading: false,

  setUser: (user) => set({ user }),
  setLoading: (loading) => set({ loading }),
  isLoggedIn: () => get().user !== null,
  logout: () => set({ user: null }),
}));

if (process.env.NODE_ENV === 'development') {
  mountStoreDevtool('Auth Store', useAuthStore);
}
