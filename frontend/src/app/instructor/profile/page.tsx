"use client";

import { useState, useEffect } from "react";
import { User } from "@/types";
import { useRouter } from "next/navigation";
import MainLayout from "@/components/layouts/MainLayout";
import Sidebar from "@/components/instructor/Sidebar";
import Header from "@/components/instructor/Header";
import { useAuthStore } from "@/store/auth";
import useAxios from "@/utils/axios";
import { toast } from "react-hot-toast";

export default function Profile() {
  const [profile, setProfile] = useState<User | null>(null);
  const [imagePreview, setImagePreview] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    if (!user?.user_id) {
      router.push('/login');
      return;
    }
    fetchProfile();
  }, [user]);

  const fetchProfile = async () => {
    try {
      const response = await useAxios.get(`user/profile/${user?.user_id}`);
      setProfile(response.data);
      setImagePreview(response.data.image);
    } catch (error) {
      console.error(error);
      toast.error("Failed to load profile");
    }
  };

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const formData = new FormData();
      Object.entries(profile || {}).forEach(([key, value]) => {
        formData.append(key, value);
      });

      await useAxios.put(`user/profile/${user?.user_id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      toast.success("Profile updated successfully");
    } catch (error) {
      console.error(error);
      toast.error("Failed to update profile");
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      setProfile(prev => prev ? {...prev, image: file} : null);
    }
  };

  return (
    <MainLayout>
      <div className="container max-w-7xl mx-auto px-4 py-8">
        <Header />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-8">
          <Sidebar />
          <div className="col-span-3">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-2xl font-semibold mb-6">Profile Settings</h2>
              
              <form onSubmit={handleProfileUpdate}>
                {/* Profile Image */}
                <div className="mb-6">
                  <div className="flex items-center">
                    <img 
                      src={imagePreview || '/placeholder.png'} 
                      alt="Profile"
                      className="w-24 h-24 rounded-full object-cover"
                    />
                    <div className="ml-4">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageChange}
                        className="hidden"
                        id="profile-image"
                      />
                      <label 
                        htmlFor="profile-image"
                        className="px-4 py-2 bg-gray-100 rounded-lg cursor-pointer hover:bg-gray-200"
                      >
                        Change Photo
                      </label>
                    </div>
                  </div>
                </div>

                {/* Profile Form */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Full Name
                    </label>
                    <input
                      type="text"
                      value={profile?.full_name || ''}
                      onChange={(e) => setProfile(prev => 
                        prev ? {...prev, full_name: e.target.value} : null
                      )}
                      className="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      About
                    </label>
                    <textarea
                      value={profile?.about || ''}
                      onChange={(e) => setProfile(prev => 
                        prev ? {...prev, about: e.target.value} : null
                      )}
                      rows={4}
                      className="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Country
                    </label>
                    <input
                      type="text"
                      value={profile?.country || ''}
                      onChange={(e) => setProfile(prev => 
                        prev ? {...prev, country: e.target.value} : null
                      )}
                      className="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {isLoading ? 'Updating...' : 'Update Profile'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
} 