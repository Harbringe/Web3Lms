export interface User {
  user_id: string;
  email: string;
  full_name: string;
  teacher_id?: string;
  image?: string;
  about?: string;
  country?: string;
}

export interface Course {
  course_id: string;
  title: string;
  description: string;
  image: string;
  file?: string;
  level: 'Beginner' | 'Intermediate' | 'Advanced';
  language: string;
  price: number;
  category: Category;
  students?: Student[];
  date: string;
  teacher_course_status?: string;
}

export interface Category {
  id: number;
  title: string;
}

export interface Student {
  id: string;
  name: string;
}

export interface Order {
  oid: string;
  course: Course;
  price: number;
  date: string;
}

export interface Stats {
  total_courses: number;
  total_students: number;
  total_earnings: number;
  total_reviews: number;
} 