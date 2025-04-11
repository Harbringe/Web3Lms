"use client";

import { useEffect } from "react";
import { setUser } from "@/utils/auth";
import Link from "next/link";
import { useAuthStore } from "@/store/auth";

export default function Home() {
  const isLoggedIn = useAuthStore((state) => state.isLoggedIn);

  useEffect(() => {
    setUser();
  }, []);

  return (
    <main className="min-h-screen p-8">
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold mb-8">Welcome to Our App</h1>
        
        {!isLoggedIn() ? (
          <div className="space-x-4">
            <Link 
              href="/login" 
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Login
            </Link>
            <Link 
              href="/register" 
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
              Register
            </Link>
          </div>
        ) : (
          <div>
            <p className="mb-4">You are logged in!</p>
            <Link 
              href="/logout" 
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            >
              Logout
            </Link>
          </div>
        )}
      </div>
    </main>
  );
}
