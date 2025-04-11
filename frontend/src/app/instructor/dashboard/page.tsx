"use client";

import { useState, useEffect } from "react";
import { Course, Stats } from "@/types";
import moment from "moment";
import { useRouter } from "next/navigation";

import Sidebar from "@/components/instructor/Sidebar";
import Header from "@/components/instructor/Header";
import MainLayout from "@/components/layouts/MainLayout";
import useAxios from "@/utils/axios";
import { useAuthStore } from "@/store/auth";

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const router = useRouter();
  const user = useAuthStore((state) => state.user);

  const fetchData = async () => {
    try {
      const [statsRes, coursesRes] = await Promise.all([
        useAxios.get(`teacher/summary/${user?.teacher_id}`),
        useAxios.get(`teacher/course-lists/${user?.teacher_id}`)
      ]);
      
      setStats(statsRes.data[0]);
      setCourses(coursesRes.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    if (!user?.teacher_id) {
      router.push('/login');
      return;
    }
    fetchData();
  }, [user]);

  const filteredCourses = courses.filter(course => 
    course.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <MainLayout>
      <div className="container max-w-7xl mx-auto px-4 py-8">
        <Header />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-8">
          <Sidebar />
          <div className="col-span-3">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <StatCard 
                title="Total Courses"
                value={stats?.total_courses || 0}
                icon="book"
              />
              <StatCard 
                title="Total Students"
                value={stats?.total_students || 0}
                icon="users"
              />
              <StatCard 
                title="Total Earnings"
                value={`$${stats?.total_earnings?.toFixed(2) || 0}`}
                icon="dollar"
              />
              <StatCard 
                title="Total Reviews"
                value={stats?.total_reviews || 0}
                icon="star"
              />
            </div>

            {/* Course List */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold">Your Courses</h2>
                <input
                  type="search"
                  placeholder="Search courses..."
                  className="px-4 py-2 border rounded-lg"
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-4">Course</th>
                      <th className="text-left py-4">Students</th>
                      <th className="text-left py-4">Level</th>
                      <th className="text-left py-4">Date</th>
                      <th className="text-left py-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredCourses.map((course) => (
                      <CourseRow key={course.course_id} course={course} />
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}

interface StatCardProps {
  title: string;
  value: number | string;
  icon: string;
}

function StatCard({ title, value, icon }: StatCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center">
        <div className={`w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center`}>
          <i className={`fas fa-${icon} text-indigo-600 text-xl`} />
        </div>
        <div className="ml-4">
          <h3 className="text-sm text-gray-500">{title}</h3>
          <p className="text-2xl font-semibold">{value}</p>
        </div>
      </div>
    </div>
  );
}

interface CourseRowProps {
  course: Course;
}

function CourseRow({ course }: CourseRowProps) {
  return (
    <tr className="border-b hover:bg-gray-50">
      <td className="py-4">
        <div className="flex items-center">
          <img 
            src={course.image} 
            alt={course.title}
            className="w-12 h-12 rounded-lg object-cover"
          />
          <div className="ml-4">
            <h4 className="font-medium">{course.title}</h4>
            <p className="text-sm text-gray-500">${course.price}</p>
          </div>
        </div>
      </td>
      <td className="py-4">{course.students?.length || 0}</td>
      <td className="py-4">
        <span className="px-3 py-1 rounded-full bg-green-100 text-green-800">
          {course.level}
        </span>
      </td>
      <td className="py-4">{moment(course.date).format("DD MMM, YYYY")}</td>
      <td className="py-4">
        <div className="flex space-x-2">
          <button className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg">
            <i className="fas fa-edit" />
          </button>
          <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg">
            <i className="fas fa-trash" />
          </button>
          <button className="p-2 text-gray-600 hover:bg-gray-50 rounded-lg">
            <i className="fas fa-eye" />
          </button>
        </div>
      </td>
    </tr>
  );
} 