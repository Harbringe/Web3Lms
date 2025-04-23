from django.test import TestCase
from django.contrib.auth import get_user_model
from api.serializer import RegisterSerializer, FileUploadSerializer
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model() 


class RegisterSerializerTestCase(TestCase):

    def test_register_serializer_valid_data(self):
        data = {
            "full_name": "Arjun Athare",
            "email": "arjun@example.com",
            "password": "StrongP@ssword123",
            "password2": "StrongP@ssword123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()
        self.assertEqual(user.full_name, "Arjun Athare")
        self.assertEqual(user.email, "arjun@example.com")
        self.assertEqual(user.username, "arjun")
        self.assertTrue(user.check_password("StrongP@ssword123"))

    def test_register_serializer_password_mismatch(self):
        data = {
            "email": "mismatch@example.com",
            "password": "TestPassword123",
            "password2": "WrongPassword123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_register_serializer_missing_fields(self):
        data = {
            "email": "missingfields@example.com",
            "password": "SomePass123",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password2", serializer.errors)

    def test_register_serializer_weak_password(self):
        data = {
            "full_name": "Weak Pass",
            "email": "weak@example.com",
            "password": "123",
            "password2": "123", 
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)


class FileUploadSerializerTestCase(TestCase):

    def test_file_upload_serializer_valid_file(self):
        file = SimpleUploadedFile("dummy.txt", b"file content")
        data = {"file": file}
        serializer = FileUploadSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["file"].name, "dummy.txt")

    def test_file_upload_serializer_missing_file(self):
        serializer = FileUploadSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn("file", serializer.errors)
