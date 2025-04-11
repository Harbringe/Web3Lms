"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";
import { EnvelopeIcon, ArrowLeftIcon } from "@heroicons/react/24/outline";
import { toast } from "react-hot-toast";
import useAxios from "@/utils/axios";
import { Button, Input, Card } from "@/components/ui";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isEmailSent, setIsEmailSent] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await useAxios.get(`user/password-reset/${email}/`);
      setIsEmailSent(true);
      toast.success("Password reset email sent successfully");
    } catch (error) {
      console.error(error);
      toast.error("Failed to send reset email");
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
            <h1 className="text-2xl font-bold mb-2">Forgot Password</h1>
            <p className="text-gray-600">
              Enter your email and we'll send you instructions to reset your password
            </p>
          </div>

          {!isEmailSent ? (
            <form onSubmit={handleSubmit}>
              <Input
                type="email"
                label="Email Address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                icon={<EnvelopeIcon className="w-5 h-5 text-gray-400" />}
                required
              />

              <Button
                type="submit"
                className="w-full mt-6"
                loading={isLoading}
              >
                Send Reset Link
              </Button>
            </form>
          ) : (
            <div className="text-center">
              <div className="bg-green-50 text-green-800 p-4 rounded-lg mb-6">
                Check your email for password reset instructions
              </div>
              <Button
                variant="outlined"
                onClick={() => router.push('/login')}
                className="w-full"
              >
                Return to Login
              </Button>
            </div>
          )}

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