import datetime
from django.test import TestCase
from userauths.models import User
from api.models import Teacher, Course, CartOrderItem, CartOrder, Category

class TeacherModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com', username='testuser', password='password123')
        self.teacher = Teacher.objects.create(user=self.user, full_name="John Doe", wallet_address="0x1234567890abcdef")
        self.category = Category.objects.create(title="Test Category")
        self.course = Course.objects.create(
            category=self.category, 
            teacher=self.teacher, 
            title="Test Course", 
            date = datetime.datetime.now(),
            description="Test Description",
            price=100.0
        )


    def test_teacher_str_method_returns_full_name(self):
        self.assertEqual(str(self.teacher), "John Doe")

    
