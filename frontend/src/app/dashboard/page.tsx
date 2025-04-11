"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { logout } from "@/utils/auth";
import {
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  EnvelopeIcon,
  IdentificationIcon,
} from "@heroicons/react/24/outline";

export default function Dashboard() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const isLoggedIn = useAuthStore((state) => state.isLoggedIn);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/login");
    }
  }, [isLoggedIn, router]);

  const handleLogout = async () => {
    logout();
    router.push("/login");
  };

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-white rounded-2xl shadow-xl overflow-hidden"
        >
          {/* Header Section */}
          <div className="bg-gradient-to-r from-indigo-600 to-cyan-600 px-6 py-8 sm:px-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="bg-white p-2 rounded-full">
                  <UserCircleIcon className="w-12 h-12 text-indigo-600" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">
                    Welcome, {user.full_name}
                  </h1>
                  <p className="text-indigo-100">Dashboard</p>
                </div>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleLogout}
                className="flex items-center space-x-2 bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg transition-colors duration-200"
              >
                <ArrowRightOnRectangleIcon className="w-5 h-5" />
                <span>Logout</span>
              </motion.button>
            </div>
          </div>

          {/* Content Section */}
          <div className="px-6 py-8 sm:px-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* User Details Card */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-gray-50 rounded-xl p-6"
              >
                <h2 className="text-xl font-semibold text-gray-800 mb-4">
                  User Details
                </h2>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <IdentificationIcon className="w-5 h-5 text-indigo-600" />
                    <div>
                      <p className="text-sm text-gray-500">User ID</p>
                      <p className="text-gray-800">{user.user_id}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <EnvelopeIcon className="w-5 h-5 text-indigo-600" />
                    <div>
                      <p className="text-sm text-gray-500">Email</p>
                      <p className="text-gray-800">{user.email}</p>
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Activity Card */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-gray-50 rounded-xl p-6"
              >
                <h2 className="text-xl font-semibold text-gray-800 mb-4">
                  Recent Activity
                </h2>
                <div className="text-gray-600">
                  <p>No recent activity to display.</p>
                </div>
              </motion.div>
            </div>

            {/* Additional Content */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="mt-6 bg-gray-50 rounded-xl p-6"
            >
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Quick Actions
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                <button className="p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 text-left">
                  <h3 className="font-medium text-gray-800">Edit Profile</h3>
                  <p className="text-sm text-gray-500">
                    Update your personal information
                  </p>
                </button>
                <button className="p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 text-left">
                  <h3 className="font-medium text-gray-800">Security</h3>
                  <p className="text-sm text-gray-500">
                    Manage your security settings
                  </p>
                </button>
                <button className="p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 text-left">
                  <h3 className="font-medium text-gray-800">Preferences</h3>
                  <p className="text-sm text-gray-500">
                    Customize your experience
                  </p>
                </button>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
  );
} 