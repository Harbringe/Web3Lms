"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const isLoggedIn = useAuthStore((state) => state.isLoggedIn);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push('/login');
    }
  }, [isLoggedIn, router]);

  if (!isLoggedIn()) {
    return null;
  }

  return <>{children}</>;
} 