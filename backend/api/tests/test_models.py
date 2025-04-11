from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import Teacher, Course, CartOrderItem
from decimal import Decimal

User = get_user_model()

class TeacherModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            full_name='Test User',
            username='test_user',
            email='test@example.com',
            password='TestPassword123!'
        )
        self.teacher = Teacher.objects.create(
            user=self.user,
            full_name='Test Teacher',
            bio='Test Bio',
            facebook='https://facebook.com/test',
            twitter='https://twitter.com/test',
            linkedin='https://linkedin.com/test',
            about='Test About',
            country='Test Country',
            wallet_address='test-addr1qxy2k7y4nj0q12cuq7phmdg73y6jndelcmya5nq7eyqvvj2lzkfj69x6xq38z8'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            teacher=self.teacher,
            price=Decimal('99.99'),
            platform_status='Published',
            teacher_course_status='Published'
        )
        self.cart_order_item = CartOrderItem.objects.create(
            teacher=self.teacher,
            course=self.course,
            price=Decimal('99.99')
        )

    # Positive Tests
    def test_teacher_full_name(self):
        self.assertEqual(self.teacher.full_name, 'Test Teacher')
    
    def test_teacher_bio(self):
        self.assertEqual(self.teacher.bio, 'Test Bio')
    
    def test_teacher_wallet_address(self):
        self.assertEqual(self.teacher.wallet_address, 'test-addr1qxy2k7y4nj0q12cuq7phmdg73y6jndelcmya5nq7eyqvvj2lzkfj69x6xq38z8')
    
    def test_teacher_str_method(self):
        self.assertEqual(str(self.teacher), 'Test Teacher')
    
    def test_teacher_students_count(self):
        students = self.teacher.students()
        self.assertEqual(students.count(), 1)

    def test_teacher_students_content(self):
        students = self.teacher.students()
        self.assertEqual(students.first(), self.cart_order_item)

    def test_teacher_courses_count(self):
        courses = self.teacher.courses()
        self.assertEqual(courses.count(), 1)
    
    def test_teacher_courses_content(self):
        courses = self.teacher.courses()
        self.assertEqual(courses.first(), self.course)
    
    def test_teacher_review_count(self):
        self.assertEqual(self.teacher.review(), 1)
    
    def test_teacher_default_image(self):
        self.assertEqual(self.teacher.image.name, 'default.jpg')

    # Negative Tests
    def test_teacher_duplicate_wallet_address(self):
        with self.assertRaises(Exception):
            Teacher.objects.create(
                user=User.objects.create_user(
                    full_name='Another User',
                    email='another@example.com',
                    password='TestPassword123!'
                ),
                full_name='Another Teacher',
                wallet_address=self.teacher.wallet_address
            )

    def test_teacher_missing_wallet_address(self):
        with self.assertRaises(Exception):
            Teacher.objects.create(
                user=User.objects.create_user(
                    full_name='Another User',
                    email='another@example.com',
                    password='TestPassword123!'
                ),
                full_name='Another Teacher'
            )
    
    def test_teacher_missing_user(self):
        with self.assertRaises(Exception):
            Teacher.objects.create(
                full_name='Another Teacher',
                wallet_address='unique-wallet-address'
            )

    # Sanity Tests
    def test_teacher_optional_bio(self):
        teacher = Teacher.objects.create(
            user=User.objects.create_user(
                full_name='Optional User',
                email='optional@example.com',
                password='TestPassword123!'
            ),
            full_name='Optional Teacher',
            wallet_address='wallet-optional-1'
        )
        self.assertIsNone(teacher.bio)
    
    def test_teacher_optional_facebook(self):
        teacher = Teacher.objects.get(full_name='Optional Teacher')
        self.assertIsNone(teacher.facebook)

    def test_teacher_optional_twitter(self):
        teacher = Teacher.objects.get(full_name='Optional Teacher')
        self.assertIsNone(teacher.twitter)

    def test_teacher_optional_linkedin(self):
        teacher = Teacher.objects.get(full_name='Optional Teacher')
        self.assertIsNone(teacher.linkedin)

    def test_teacher_optional_about(self):
        teacher = Teacher.objects.get(full_name='Optional Teacher')
        self.assertIsNone(teacher.about)

    def test_teacher_optional_country(self):
        teacher = Teacher.objects.get(full_name='Optional Teacher')
        self.assertIsNone(teacher.country)
    
    def test_teacher_cascade_on_user_delete(self):
        user_id = self.user.id
        self.user.delete()
        self.assertFalse(Teacher.objects.filter(user_id=user_id).exists())
    
    def test_teacher_image_upload(self):
        image_content = b'fake image content'
        image = SimpleUploadedFile("test_image.jpg", image_content, content_type="image/jpeg")
        teacher = Teacher.objects.create(
            user=User.objects.create_user(
                full_name='Image User',
                email='image@example.com',
                password='TestPassword123!'
            ),
            full_name='Image Teacher',
            wallet_address='wallet-image-upload',
            image=image
        )
        self.assertTrue(teacher.image)

    def test_teacher_image_name_not_default(self):
        teacher = Teacher.objects.get(full_name='Image Teacher')
        self.assertNotEqual(teacher.image.name, 'default.jpg')
