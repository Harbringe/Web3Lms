from rest_framework.test import APITestCase as TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from userauths.models import User, Profile


class UserModelCorrectInputTests(TestCase):
    def test_user_email_saved_correctly(self):
        user = User.objects.create_user(email='test@example.com', username='testuser', password='pass1234')
        self.assertEqual(user.email, 'test@example.com')

    def test_user_username_saved_correctly(self):
        user = User.objects.create_user(email='test@example.com', username='testuser', password='pass1234')
        self.assertEqual(user.username, 'testuser')

    def test_user_password_is_hashed_correctly(self):
        user = User.objects.create_user(email='test@example.com', username='testuser', password='pass1234')
        self.assertTrue(user.check_password('pass1234'))

    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user(email='auto@example.com', username='autouser', password='pass1234')
        self.assertIsNotNone(user.profile)

    def test_profile_user_relation_is_correct(self):
        user = User.objects.create_user(email='auto@example.com', username='autouser', password='pass1234')
        self.assertEqual(user.profile.user, user)


class UserModelWrongInputTests(TestCase):
    
    def test_duplicate_email_raises_integrity_error(self):
        User.objects.create_user(email='dup@example.com', username='user1', password='pass1234')
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email='dup@example.com', username='user2', password='pass1234')

    def test_duplicate_username_raises_integrity_error(self):
        User.objects.create_user(email='one@example.com', username='sameuser', password='pass1234')
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email='two@example.com', username='sameuser', password='pass5678')


class SanityTests(TestCase):
    def test_user_str_returns_email(self):
        user = User.objects.create_user(email='str@example.com', username='strtest', password='pass1234')
        self.assertEqual(str(user), 'str@example.com')

    def test_profile_str_returns_full_name(self):
        user = User.objects.create_user(email='fullname@example.com', username='fullnameuser', password='pass1234')
        profile = user.profile
        profile.full_name = "John Doe"
        profile.save()
        self.assertEqual(str(profile), 'John Doe')

    def test_profile_str_uses_user_fullname_if_profile_name_blank(self):
        user = User.objects.create_user(email='blank@example.com', username='blankuser', password='pass1234')
        user.full_name = 'Backup Name'
        user.save()
        profile = user.profile
        profile.full_name = ""
        profile.save()
        self.assertEqual(str(profile), 'Backup Name')

    def test_username_auto_generated_from_email(self):
        user = User.objects.create(email='auto_username@example.com', password='pass1234')
        user.save()
        self.assertEqual(user.username, 'auto_username')
