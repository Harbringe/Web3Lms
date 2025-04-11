"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";
import { LockClosedIcon, ArrowLeftIcon } from "@heroicons/react/24/outline";
import { toast } from "react-hot-toast";
import useAxios from "@/utils/axios";
import { Button, Input, Card } from "@/components/ui";

export default function ResetPassword() {
  const [passwords, setPasswords] = useState({
    password: "",
    confirmPassword: ""
  });
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  const otp = searchParams.get("otp");
  const uuidb64 = searchParams.get("uuidb64");
  const refresh_token = searchParams.get("refresh_token");

  useEffect(() => {
    if (!otp || !uuidb64 || !refresh_token) {
      toast.error("Invalid reset link");
      router.push('/login');
    }
  }, [otp, uuidb64, refresh_token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwords.password !== passwords.confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    setIsLoading(true);

    const formData = new FormData();
    formData.append("password", passwords.password);
    formData.append("otp", otp as string);
    formData.append("uuidb64", uuidb64 as string);
    formData.append("refresh_token", refresh_token as string);

    try {
      const response = await useAxios.post("user/password-change/", formData);
      toast.success("Password changed successfully");
      router.push('/login');
    } catch (error) {
      console.error(error);
      toast.error("Failed to change password");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 flex items-center justify-center">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <Card className="p-8">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold mb-2">Reset Password</h1>
            <p className="text-gray-600">
              Enter your new password
            </p>
          </div>

          <form onSubmit={handleSubmit}>
            <Input
              type="password"
              label="New Password"
              value={passwords.password}
              onChange={(e) => setPasswords(prev => ({
                ...prev,
                password: e.target.value
              }))}
              icon={<LockClosedIcon className="w-5 h-5 text-gray-400" />}
              required
            />

            <Input
              type="password"
              label="Confirm New Password"
              value={passwords.confirmPassword}
              onChange={(e) => setPasswords(prev => ({
                ...prev,
                confirmPassword: e.target.value
              }))}
              icon={<LockClosedIcon className="w-5 h-5 text-gray-400" />}
              required
              className="mt-4"
            />

            <Button
              type="submit"
              className="w-full mt-6"
              loading={isLoading}
            >
              Reset Password
            </Button>
          </form>

          <div className="mt-6 text-center">
            <Link 
              href="/login"
              className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
            >
              <ArrowLeftIcon className="w-4 h-4 mr-2" />
              Back to Login
            </Link>
          </div>
        </Card>
      </motion.div>
    </div>
  );
} 