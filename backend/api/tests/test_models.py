from django.test import TestCase
from userauths.models import User
from api.models import Teacher, Course, CartOrderItem, CartOrder

class TeacherModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@example.com', username='testuser', password='password123')
        self.teacher = Teacher.objects.create(user=self.user, full_name="John Doe", wallet_address="0x1234567890abcdef")
        self.cate


    def test_teacher_str_method_returns_full_name(self):
        self.assertEqual(str(self.teacher), "John Doe")

    # students() with correct data
    def test_students_method_returns_correct_cartorderitems(self):
        course = Course.objects.create(
            teacher=self.teacher,
            title="Test Course",
            nft_id="UNIQUE_NFT_ID_123"
        )

        # Create required CartOrder
        order = CartOrder.objects.create(
            user=self.user,
            price=0.00
        )

        # Create CartOrderItem
        CartOrderItem.objects.create(
            order=order,
            course=course,
            teacher=self.teacher
        )

        self.assertEqual(self.teacher.students().count(), 1)

    # # students() with no CartOrderItem
    # def test_students_method_returns_zero_if_none(self):
    #     self.assertEqual(self.teacher.students().count(), 0)

    # # courses() with correct data
    # def test_courses_method_returns_correct_courses(self):
    #     Course.objects.create(title="Math 101", teacher=self.teacher)
    #     self.assertEqual(self.teacher.courses().count(), 1)

    # # courses() with no course
    # def test_courses_method_returns_zero_if_none(self):
    #     self.assertEqual(self.teacher.courses().count(), 0)

    # # review() returns total number of courses
    # def test_review_method_returns_total_course_count(self):
    #     Course.objects.create(title="Physics", teacher=self.teacher)
    #     self.assertEqual(self.teacher.review(), 1)

    # # test if wallet_address is enforced as unique
    # def test_wallet_address_unique_constraint(self):
    #     with self.assertRaises(Exception):
    #         Teacher.objects.create(
    #             user=User.objects.create_user(username='anotheruser'),
    #             full_name="Jane",
    #             wallet_address="0x1234567890abcdef"
    #         )

    # # sanitation/security: test if HTML in full_name is stored as-is (escaping is front-end job)
    # def test_full_name_allows_html_but_stores_as_is(self):
    #     self.teacher.full_name = "<script>alert('XSS')</script>"
    #     self.teacher.save()
    #     self.assertIn("<script>", self.teacher.full_name)


