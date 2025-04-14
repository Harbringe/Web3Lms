from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import Teacher, Course, CartOrderItem
from decimal import Decimal

User = get_user_model()

class TeacherModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.teacher = Teacher.objects.create(
            user=self.user,
            full_name="John Doe",
            wallet_address="unique_wallet_123"
        )

    # === __str__ ===

    def test_str_returns_full_name(self):
        self.assertEqual(str(self.teacher), "John Doe")

    def test_str_returns_empty_if_no_name(self):
        self.teacher.full_name = ""
        self.teacher.save()
        self.assertEqual(str(self.teacher), "")

    def test_str_sanity_not_none(self):
        self.assertIsNotNone(str(self.teacher))

    # === students() ===

    def test_students_with_valid_cart_items(self):
        CartOrderItem.objects.create(teacher=self.teacher)
        self.assertEqual(self.teacher.students().count(), 1)

    def test_students_with_no_cart_items(self):
        self.assertEqual(self.teacher.students().count(), 0)

    def test_students_wrong_teacher(self):
        other_teacher = Teacher.objects.create(
            user=User.objects.create_user(username="other", password="pass123"),
            full_name="Other Teacher",
            wallet_address="wallet_other"
        )
        CartOrderItem.objects.create(teacher=other_teacher)
        self.assertEqual(self.teacher.students().count(), 0)

    # === courses() ===

    def test_courses_with_valid_courses(self):
        Course.objects.create(teacher=self.teacher)
        self.assertEqual(self.teacher.courses().count(), 1)

    def test_courses_with_no_courses(self):
        self.assertEqual(self.teacher.courses().count(), 0)

    def test_courses_invalid_teacher(self):
        another_teacher = Teacher.objects.create(
            user=User.objects.create_user(username="another", password="pass123"),
            full_name="Another Teacher",
            wallet_address="another_wallet_123"
        )
        Course.objects.create(teacher=another_teacher)
        self.assertEqual(self.teacher.courses().count(), 0)

    # === review() ===

    def test_review_count_is_correct(self):
        Course.objects.create(teacher=self.teacher)
        Course.objects.create(teacher=self.teacher)
        self.assertEqual(self.teacher.review(), 2)

    def test_review_count_zero(self):
        self.assertEqual(self.teacher.review(), 0)

    def test_review_count_wrong_teacher(self):
        other = Teacher.objects.create(
            user=User.objects.create_user(username="wrong", password="pass"),
            full_name="Wrong Teacher",
            wallet_address="wallet_wrong"
        )
        Course.objects.create(teacher=other)
        self.assertEqual(self.teacher.review(), 0)
