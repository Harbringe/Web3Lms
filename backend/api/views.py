from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.db import models
from django.db.models.functions import ExtractMonth
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from api import serializer as api_serializer
from api import models as api_models
from userauths.models import User, Profile
from api.models import LEVEL, LANGUAGE

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, APIView


import random
from decimal import Decimal
# import stripe
import requests
from datetime import datetime, timedelta
from distutils.util import strtobool


# Updates
from django.core.files.storage import default_storage
import os
from moviepy import VideoFileClip
from django.core.files.base import ContentFile
import math
from rest_framework.parsers import MultiPartParser, FormParser
import uuid
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import razorpay

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# stripe.api_key = settings.STRIPE_SECRET_KEY
PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
PAYPAL_SECRET_ID = settings.PAYPAL_SECRET_ID



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializer.MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = api_serializer.RegisterSerializer

def generate_random_otp(length=7):
    otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return otp

class PasswordResetEmailVerifyAPIView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def get_object(self):
        email = self.kwargs['email'] 

        user = User.objects.filter(email=email).first()

        if user:
            uuidb64 = user.pk
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh.access_token)

            user.refresh_token = refresh_token
            user.otp = generate_random_otp()
            user.save()

            link = f"https://web3lmsfrontendcardano.vercel.app/create-new-password/?otp={user.otp}&uuidb64={uuidb64}&refresh_token={refresh_token}"

            context = {
                "link": link,
                "username": user.username
            }

            subject = "Password Rest Email"
            text_body = render_to_string("email/password_reset.txt", context)
            html_body = render_to_string("email/password_reset.html", context)

            msg = EmailMultiAlternatives(
                subject=subject,
                from_email=settings.FROM_EMAIL,
                to=[user.email],
                body=text_body
            )

            msg.attach_alternative(html_body, "text/html")
            msg.send()

            print("link ======", link)
        return user
    
class PasswordChangeAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer

    def create(self, request, *args, **kwargs):
        otp = request.data['otp']
        uuidb64 = request.data['uuidb64']
        password = request.data['password']

        user = User.objects.get(id=uuidb64, otp=otp)
        if user:
            user.set_password(password)
            # user.otp = ""
            user.save()

            return Response({"message": "Password Changed Successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "User Does Not Exists"}, status=status.HTTP_404_NOT_FOUND)

class ChangePasswordAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        old_password = request.data['old_password']
        new_password = request.data['new_password']

        user = User.objects.get(id=user_id)
        if user is not None:
            if check_password(old_password, user.password):
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password changed successfully", "icon": "success"})
            else:
                return Response({"message": "Old password is incorrect", "icon": "warning"})
        else:
            return Response({"message": "User does not exists", "icon": "error"})

class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = api_serializer.ProfileSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        try:
            user_id = self.kwargs['user_id']
            user = User.objects.get(id=user_id)
            return Profile.objects.get(user=user)
        except:
            return None

class CategoryListAPIView(generics.ListAPIView):
    queryset = api_models.Category.objects.filter(active=True)  
    serializer_class = api_serializer.CategorySerializer
    permission_classes = [AllowAny]

class CourseListAPIView(generics.ListAPIView):
    queryset = api_models.Course.objects.filter(platform_status="Published", teacher_course_status="Published")
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]

class TeacherCourseDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]
    queryset = api_models.Course.objects.filter(platform_status="Published", teacher_course_status="Published")

    def get_object(self):
        course_id = self.kwargs['course_id']
        course = api_models.Course.objects.get(course_id=course_id)
        return course
    
def get_tax_rate(country_name):
    """Helper function to get tax rate for a country"""
    try:
        country_object = api_models.Country.objects.filter(name=country_name).first()
        if country_object:
            return Decimal(country_object.tax_rate) / Decimal(100)
        return Decimal('0')
    except:
        return Decimal('0')

class CartAPIView(generics.CreateAPIView):
    queryset = api_models.Cart.objects.all()
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        course_id = request.data['course_id']  
        user_id = request.data['user_id']
        price = request.data['price']
        country_name = request.data['country_name']
        cart_id = request.data['cart_id']

        print("course_id ==========", course_id)

        course = api_models.Course.objects.filter(id=course_id).first()
        
        if user_id != "undefined":
            user = User.objects.filter(id=user_id).first()
        else:
            user = None

        # Get country and tax rate
        country_object = api_models.Country.objects.filter(name=country_name).first()
        country = country_object.name if country_object else "United States"
        tax_rate = get_tax_rate(country)
        
        # Calculate tax and total
        price_decimal = Decimal(str(price))
        tax_fee = price_decimal * tax_rate
        total = price_decimal + tax_fee

        cart = api_models.Cart.objects.filter(cart_id=cart_id, course=course).first()

        if cart:
            cart.course = course
            cart.user = user
            cart.price = price
            cart.tax_fee = tax_fee
            cart.country = country
            cart.cart_id = cart_id
            cart.total = total
            cart.save()

            return Response({"message": "Cart Updated Successfully"}, status=status.HTTP_200_OK)

        else:
            cart = api_models.Cart.objects.create(
                course=course,
                user=user,
                price=price,
                tax_fee=tax_fee,
                country=country,
                cart_id=cart_id,
                total=total
            )

            return Response({"message": "Cart Created Successfully"}, status=status.HTTP_201_CREATED)

class CartListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        queryset = api_models.Cart.objects.filter(cart_id=cart_id)
        return queryset

class CartItemDeleteAPIView(generics.DestroyAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        cart_id = self.kwargs['cart_id']
        item_id = self.kwargs['item_id']

        return api_models.Cart.objects.filter(cart_id=cart_id, id=item_id).first()

class CartStatsAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]
    lookup_field = 'cart_id'

    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        queryset = api_models.Cart.objects.filter(cart_id=cart_id)
        return queryset
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        total_price = 0.00
        total_tax = 0.00
        total_total = 0.00

        for cart_item in queryset:
            total_price += float(self.calculate_price(cart_item))
            total_tax += float(self.calculate_tax(cart_item))
            total_total += round(float(self.calculate_total(cart_item)), 2)

        data = {
            "price": total_price,
            "tax": total_tax,
            "total": total_total,
        }

        return Response(data)

    def calculate_price(self, cart_item):
        return cart_item.price
    
    def calculate_tax(self, cart_item):
        return cart_item.tax_fee

    def calculate_total(self, cart_item):
        return cart_item.total

class CreateOrderAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        print(request.headers.get('Authorization'))
        full_name = request.data['full_name']
        email = request.data['email']
        country = request.data['country']
        cart_id = request.data['cart_id']
        user_id = request.user.id

        if user_id != 0:
            user = User.objects.get(id=user_id)
        else:
            user = None

        cart_items = api_models.Cart.objects.filter(cart_id=cart_id)

        total_price = Decimal('0.00')
        total_tax = Decimal('0.00')
        total_initial_total = Decimal('0.00')
        total_total = Decimal('0.00')

        order = api_models.CartOrder.objects.create(
            full_name=full_name,
            email=email,
            country=country,
            student=user
        )

        for c in cart_items:
            # Recalculate tax to ensure consistency
            tax_rate = get_tax_rate(c.country)
            price_decimal = Decimal(str(c.price))
            tax_fee = price_decimal * tax_rate
            total = price_decimal + tax_fee

            api_models.CartOrderItem.objects.create(
                order=order,
                course=c.course,
                price=price_decimal,
                tax_fee=tax_fee,
                total=total,
                initial_total=total,
                teacher=c.course.teacher
            )

            total_price += price_decimal
            total_tax += tax_fee
            total_initial_total += total
            total_total += total

            order.teachers.add(c.course.teacher)

        order.sub_total = total_price
        order.tax_fee = total_tax
        order.initial_total = total_initial_total
        order.total = total_total
        order.save()

        return Response({"message": "Order Created Successfully", "order_oid": order.oid}, status=status.HTTP_201_CREATED)

class CheckoutAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = api_models.CartOrder.objects.all()
    lookup_field = 'oid'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Get enrollment for this order
        enrollment = api_models.EnrolledCourse.objects.filter(
            order_item__order=instance
        ).first()

        # Add enrollment_id to response if found
        if enrollment:
            data['enrollment_id'] = enrollment.enrollment_id
        else:
            data['enrollment_id'] = None

        return Response(data)

class CouponApplyAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CouponSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        order_oid = request.data['order_oid']
        coupon_code = request.data['coupon_code']

        order = api_models.CartOrder.objects.get(oid=order_oid)
        coupon = api_models.Coupon.objects.filter(code=coupon_code).first()

        if coupon:
            order_items = api_models.CartOrderItem.objects.filter(order=order, teacher=coupon.teacher)
            for i in order_items:
                if not coupon in i.coupons.all():
                    discount = i.total * coupon.discount / 100

                    i.total -= discount
                    i.price -= discount
                    i.saved += discount
                    i.applied_coupon = True
                    i.coupons.add(coupon)

                    order.coupons.add(coupon)
                    order.total -= discount
                    order.sub_total -= discount
                    order.saved += discount

                    i.save()
                    order.save()
                    coupon.used_by.add(order.student)
                    return Response({"message": "Coupon Found and Activated", "icon": "success"}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message": "Coupon Already Applied", "icon": "warning"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Coupon Not Found", "icon": "error"}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
class RazorpayCheckoutAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        order_oid = self.kwargs['order_oid']
        try:
            order = api_models.CartOrder.objects.get(oid=order_oid)
        except api_models.CartOrder.DoesNotExist:
            return Response({"message": "Order Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Create Razorpay Order
            razorpay_order = razorpay_client.order.create({
                'amount': float(order.total) * 100, 
                'currency': 'INR',
                'receipt': order.oid,
                'payment_capture': '1'
            })

            order.razorpay_order_id = razorpay_order['id']
            order.save()

            # Prepare checkout data for frontend
            checkout_data = {
                'key': settings.RAZORPAY_KEY_ID,
                'amount': float(order.total),
                'currency': 'INR',
                'name': 'Knowledge Ledger',   #TODO: CHanged this from Web3Lms to Knowledge Ledger
                'description': f'Payment for order {order.oid} of {order.total} by {order.full_name} ({order.email})',
                'order_id': razorpay_order['id'],
                'callback_url': f'{settings.FRONTEND_SITE_URL}/payment/success',
                'prefill': {
                    'name': order.full_name,
                    'email': order.email,
                },
                'notes': {
                    'order_id': order.oid,
                    'date' : order.date,
                    'full_name' : order.full_name,
                    'email': order.email,
                    'sub_total' : order.sub_total,
                    'tax_fee' : order.tax_fee,
                    'total' : order.total,
                    'country' : order.country
                },
                'theme': {
                    'color': '#4F46E5'
                }
            }

            return Response(checkout_data)
        except Exception as e:
            return Response({
                "message": f"Error creating Razorpay order: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccessAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # Get payment details from request
            payment_id = request.data.get('razorpay_payment_id')
            order_id = request.data.get('razorpay_order_id')
            signature = request.data.get('razorpay_signature')
            order_oid = request.data.get('order_oid')

            # Get the order
            order = api_models.CartOrder.objects.get(oid=order_oid)
            order_items = api_models.CartOrderItem.objects.filter(order=order)

            # Verify signature
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            }

            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
            except Exception:
                return Response({
                    'status': 'failure',
                    'message': 'Payment verification failed'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Update order
            if order.payment_status == "Processing":
                order.payment_status = "Paid"
                order.razorpay_payment_id = payment_id
                order.razorpay_signature = signature
                order.save()

                # Delete cart items after successful payment
                cart_id = None
                # Try to get cart_id from one of the order items
                if order_items.exists():
                    first_cart_item = order_items.first()
                    # Try to find the cart with this course and user to get the cart_id
                    cart = api_models.Cart.objects.filter(course=first_cart_item.course, user=order.student).first()
                    if cart:
                        cart_id = cart.cart_id
                if cart_id:
                    api_models.Cart.objects.filter(cart_id=cart_id).delete()

                # Create notifications and enrolled courses
                api_models.Notification.objects.create(
                    user=order.student,
                    order=order,
                    type="Course Enrollment Completed"
                )

                for item in order_items:
                    api_models.Notification.objects.create(
                        teacher=item.teacher,
                        order=order,
                        order_item=item,
                        type="New Order"
                    )
                    api_models.EnrolledCourse.objects.create(
                        course=item.course,
                        user=order.student,
                        teacher=item.teacher,
                        order_item=item
                    )

                return Response({
                    'status': 'success',
                    'message': 'Payment successful',
                    'order_id': order.oid,
                    'payment_id': payment_id,
                    'signature': signature
                })
            
            return Response({
                'status': 'success',
                'message': 'Payment already processed'
            })

        except api_models.CartOrder.DoesNotExist:
            return Response({
                'status': 'failure',
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'failure',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class SearchCourseAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        query = self.request.GET.get('query')
        # learn lms
        return api_models.Course.objects.filter(title__icontains=query, platform_status="Published", teacher_course_status="Published")
    
class StudentSummaryAPIView(generics.ListAPIView):
    serializer_class = api_serializer.StudentSummarySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        total_courses = api_models.EnrolledCourse.objects.filter(user=user).count()
        completed_lessons = api_models.CompletedLesson.objects.filter(user=user).count()
        achieved_certificates = api_models.Certificate.objects.filter(user=user).count()

        return [{
            "total_courses": total_courses,
            "completed_lessons": completed_lessons,
            "achieved_certificates": achieved_certificates,
        }]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class StudentCourseListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.EnrolledCourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user =  User.objects.get(id=user_id)
        return api_models.EnrolledCourse.objects.filter(user=user)

class StudentCourseDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.EnrolledCourseSerializer
    permission_classes = [AllowAny]
    lookup_field = 'enrollment_id'

    def get_object(self):
        user_id = self.kwargs['user_id']
        enrollment_id = self.kwargs['enrollment_id']

        user = User.objects.get(id=user_id)
        return api_models.EnrolledCourse.objects.get(user=user, enrollment_id=enrollment_id)
        
class StudentCourseCompletedCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CompletedLessonSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        course_id = request.data['course_id']
        variant_item_id = request.data['variant_item_id']

        user = User.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)
        variant_item = api_models.VariantItem.objects.get(variant_item_id=variant_item_id)

        completed_lessons = api_models.CompletedLesson.objects.filter(user=user, course=course, variant_item=variant_item).first()

        if completed_lessons:
            completed_lessons.delete()
            return Response({"message": "Course marked as not completed"})

        else:
            api_models.CompletedLesson.objects.create(user=user, course=course, variant_item=variant_item)
            return Response({"message": "Course marked as completed"})

class StudentNoteCreateAPIView(generics.ListCreateAPIView):
    serializer_class = api_serializer.NoteSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        enrollment_id = self.kwargs['enrollment_id']

        user = User.objects.get(id=user_id)
        enrolled = api_models.EnrolledCourse.objects.get(enrollment_id=enrollment_id)
        
        return api_models.Note.objects.filter(user=user, course=enrolled.course)

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        enrollment_id = request.data['enrollment_id']
        title = request.data['title']
        note = request.data['note']

        user = User.objects.get(id=user_id)
        enrolled = api_models.EnrolledCourse.objects.get(enrollment_id=enrollment_id)
        
        api_models.Note.objects.create(user=user, course=enrolled.course, note=note, title=title)

        return Response({"message": "Note created successfullly"}, status=status.HTTP_201_CREATED)

class StudentNoteDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['user_id']
        enrollment_id = self.kwargs['enrollment_id']
        note_id = self.kwargs['note_id']

        user = User.objects.get(id=user_id)
        enrolled = api_models.EnrolledCourse.objects.get(enrollment_id=enrollment_id)
        note = api_models.Note.objects.get(user=user, course=enrolled.course, id=note_id)
        return note

class StudentRateCourseCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.ReviewSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        course_id = request.data['course_id']
        rating = request.data['rating']
        review = request.data['review']

        user = User.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)

        api_models.Review.objects.create(
            user=user,
            course=course,
            review=review,
            rating=rating,
            active=True,
        )

        return Response({"message": "Review created successfullly"}, status=status.HTTP_201_CREATED)

class StudentRateCourseUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = api_serializer.ReviewSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        user_id = self.kwargs['user_id']
        review_id = self.kwargs['review_id']

        user = User.objects.get(id=user_id)
        return api_models.Review.objects.get(id=review_id, user=user)

class StudentWishListListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = api_serializer.WishlistSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        return api_models.Wishlist.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        course_id = request.data['course_id']

        user = User.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)

        wishlist = api_models.Wishlist.objects.filter(user=user, course=course).first()
        if wishlist:
            wishlist.delete()
            return Response({"message": "Wishlist Deleted"}, status=status.HTTP_200_OK)
        else:
            api_models.Wishlist.objects.create(
                user=user, course=course
            )
            return Response({"message": "Wishlist Created"}, status=status.HTTP_201_CREATED)

class QuestionAnswerListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = api_serializer.Question_AnswerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = api_models.Course.objects.get(id=course_id)
        return api_models.Question_Answer.objects.filter(course=course)
    
    def create(self, request, *args, **kwargs):
        course_id = request.data['course_id']
        user_id = request.data['user_id']
        title = request.data['title']
        message = request.data['message']

        user = User.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)
        
        question = api_models.Question_Answer.objects.create(
            course=course,
            user=user,
            title=title
        )

        api_models.Question_Answer_Message.objects.create(
            course=course,
            user=user,
            message=message,
            question=question
        )
        
        return Response({"message": "Group conversation Started"}, status=status.HTTP_201_CREATED)

class QuestionAnswerMessageSendAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.Question_Answer_MessageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        course_id = request.data['course_id']
        qa_id = request.data['qa_id']
        user_id = request.data['user_id']
        message = request.data['message']

        user = User.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)
        question = api_models.Question_Answer.objects.get(qa_id=qa_id)
        api_models.Question_Answer_Message.objects.create(
            course=course,
            user=user,
            message=message,
            question=question
        )

        question_serializer = api_serializer.Question_AnswerSerializer(question)
        return Response({"messgae": "Message Sent", "question": question_serializer.data})

class TeacherSummaryAPIView(generics.ListAPIView):
    serializer_class = api_serializer.TeacherSummarySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)

        one_month_ago = datetime.today() - timedelta(days=28)

        total_courses = api_models.Course.objects.filter(teacher=teacher).count()
        total_revenue = api_models.CartOrderItem.objects.filter(teacher=teacher, order__payment_status="Paid").aggregate(total_revenue=models.Sum("price"))['total_revenue'] or 0
        monthly_revenue = api_models.CartOrderItem.objects.filter(teacher=teacher, order__payment_status="Paid", date__gte=one_month_ago).aggregate(total_revenue=models.Sum("price"))['total_revenue'] or 0

        enrolled_courses = api_models.EnrolledCourse.objects.filter(teacher=teacher)
        unique_student_ids = set()
        students = []

        for course in enrolled_courses:
            if course.user_id not in unique_student_ids:
                user = User.objects.get(id=course.user_id)
                student = {
                    "full_name": user.profile.full_name,
                    "image": user.profile.image.url,
                    "country": user.profile.country,
                    "date": course.date
                }

                students.append(student)
                unique_student_ids.add(course.user_id)

        return [{
            "total_courses": total_courses,
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
            "total_students": len(students),
        }]
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class TeacherCourseListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Course.objects.filter(teacher=teacher)

class TeacherReviewListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Review.objects.filter(course__teacher=teacher)
    
class TeacherReviewDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = api_serializer.ReviewSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        teacher_id = self.kwargs['teacher_id']
        review_id = self.kwargs['review_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Review.objects.get(course__teacher=teacher, id=review_id)

class TeacherStudentsListAPIVIew(viewsets.ViewSet):
    
    def list(self, request, teacher_id=None):
        teacher = api_models.Teacher.objects.get(id=teacher_id)

        enrolled_courses = api_models.EnrolledCourse.objects.filter(teacher=teacher)
        unique_student_ids = set()
        students = []

        for course in enrolled_courses:
            if course.user_id not in unique_student_ids:
                user = User.objects.get(id=course.user_id)
                student = {
                    "full_name": user.profile.full_name,
                    "image": user.profile.image.url,
                    "country": user.profile.country,
                    "date": course.date
                }

                students.append(student)
                unique_student_ids.add(course.user_id)

        return Response(students)

@api_view(("GET", ))
def TeacherAllMonthEarningAPIView(request, teacher_id):
    teacher = api_models.Teacher.objects.get(id=teacher_id)
    monthly_earning_tracker = (
        api_models.CartOrderItem.objects
        .filter(teacher=teacher, order__payment_status="Paid")
        .annotate(
            month=ExtractMonth("date")
        )
        .values("month")
        .annotate(
            total_earning=models.Sum("price")
        )
        .order_by("month")
    )

    return Response(monthly_earning_tracker)

class TeacherBestSellingCourseAPIView(viewsets.ViewSet):

    def list(self, request, teacher_id=None):
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        courses_with_total_price = []
        courses = api_models.Course.objects.filter(teacher=teacher)

        for course in courses:
            revenue = course.enrolledcourse_set.aggregate(total_price=models.Sum('order_item__price'))['total_price'] or 0
            sales = course.enrolledcourse_set.count()

            courses_with_total_price.append({
                'course_image': course.image.url,
                'course_title': course.title,
                'revenue': revenue,
                'sales': sales,
            })

        return Response(courses_with_total_price)
    
class TeacherCourseOrdersListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CartOrderItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)

        return api_models.CartOrderItem.objects.filter(teacher=teacher)

class TeacherQuestionAnswerListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.Question_AnswerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Question_Answer.objects.filter(course__teacher=teacher)
    
class TeacherCouponListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = api_serializer.CouponSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Coupon.objects.filter(teacher=teacher)
    
class TeacherCouponDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.CouponSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        teacher_id = self.kwargs['teacher_id']
        coupon_id = self.kwargs['coupon_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Coupon.objects.get(teacher=teacher, id=coupon_id)
    
class TeacherNotificationListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Notification.objects.filter(teacher=teacher, seen=False)
    
class TeacherNotificationDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = api_serializer.NotificationSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        teacher_id = self.kwargs['teacher_id']
        noti_id = self.kwargs['noti_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)
        return api_models.Notification.objects.get(teacher=teacher, id=noti_id)
    

class CourseCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser,)

    def post(self, request):
        try:
            # Get required fields
            title = request.data.get("title")
            description = request.data.get("description")
            price = request.data.get("price")
            category_id = request.data.get("category")

            # Validate required fields
            if not all([title, description, price, category_id]):
                return Response(
                    {"error": "Missing required fields: title, description, price, category"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get optional fields
            image = request.data.get("image")
            file = request.data.get("file")
            level = request.data.get("level", "Beginner")
            language = request.data.get("language", "English")

            # Validate category exists
            try:
                category = api_models.Category.objects.get(id=category_id)
            except api_models.Category.DoesNotExist:
                return Response(
                    {"error": "Category not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get or create teacher profile
            try:
                teacher = api_models.Teacher.objects.get(user=request.user)
            except api_models.Teacher.DoesNotExist:
                return Response(
                    {"error": "Teacher profile not found. Please complete your teacher profile first."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create course
            course = api_models.Course(
                teacher=teacher,
                category=category,
                title=title,
                description=description,
                price=price,
                language=language,
                level=level,
                image=image,
                file=file,
                platform_status="Draft",  # Start as draft
                teacher_course_status="Draft"
            )
            course.save()  # Save the course first to get a primary key

            # Create notification after course is saved
            api_models.Notification.objects.create(
                teacher=teacher,
                type="Draft"
            )

            return Response({
                "message": "Course created successfully",
                "course_id": course.course_id,
                "status": "Draft",
                "slug": course.slug
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": f"An error occurred while creating the course: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class CourseUpdateAPIView(generics.RetrieveUpdateAPIView):
    querysect = api_models.Course.objects.all()
    serializer_class = api_serializer.CourseSerializer
    permisscion_classes = [AllowAny]

    def get_object(self):
        teacher_id = self.kwargs['teacher_id']
        course_id = self.kwargs['course_id']

        teacher = api_models.Teacher.objects.get(id=teacher_id)
        course = api_models.Course.objects.get(course_id=course_id)

        return course
    
    def update(self, request, *args, **kwargs):
        course = self.get_object()
        serializer = self.get_serializer(course, data=request.data)
        serializer.is_valid(raise_exception=True)

        if "image" in request.data and isinstance(request.data['image'], InMemoryUploadedFile):
            course.image = request.data['image']
        elif 'image' in request.data and str(request.data['image']) == "No File":
            course.image = None
        
        if 'file' in request.data and not str(request.data['file']).startswith("http://"):
            course.file = request.data['file']

        if 'category' in request.data['category'] and request.data['category'] != 'NaN' and request.data['category'] != "undefined":
            category = api_models.Category.objects.get(id=request.data['category'])
            course.category = category

        self.perform_update(serializer)
        self.update_variant(course, request.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update_variant(self, course, request_data):
        for key, value in request_data.items():
            if key.startswith("variants") and '[variant_title]' in key:

                index = key.split('[')[1].split(']')[0]
                title = value

                id_key = f"variants[{index}][variant_id]"
                variant_id = request_data.get(id_key)

                variant_data = {'title': title}
                item_data_list = []
                current_item = {}

                for item_key, item_value in request_data.items():
                    if f'variants[{index}][items]' in item_key:
                        field_name = item_key.split('[')[-1].split(']')[0]
                        if field_name == "title":
                            if current_item:
                                item_data_list.append(current_item)
                            current_item = {}
                        current_item.update({field_name: item_value})
                    
                if current_item:
                    item_data_list.append(current_item)

                existing_variant = course.variant_set.filter(id=variant_id).first()

                if existing_variant:
                    existing_variant.title = title
                    existing_variant.save()

                    for item_data in item_data_list[1:]:
                        preview_value = item_data.get("preview")
                        preview = bool(strtobool(str(preview_value))) if preview_value is not None else False

                        variant_item = api_models.VariantItem.objects.filter(variant_item_id=item_data.get("variant_item_id")).first()

                        if not str(item_data.get("file")).startswith("http://"):
                            if item_data.get("file") != "null":
                                file = item_data.get("file")
                            else:
                                file = None
                            
                            title = item_data.get("title")
                            description = item_data.get("description")

                            if variant_item:
                                variant_item.title = title
                                variant_item.description = description
                                variant_item.file = file
                                variant_item.preview = preview
                            else:
                                variant_item = api_models.VariantItem.objects.create(
                                    variant=existing_variant,
                                    title=title,
                                    description=description,
                                    file=file,
                                    preview=preview
                                )
                        
                        else:
                            title = item_data.get("title")
                            description = item_data.get("description")

                            if variant_item:
                                variant_item.title = title
                                variant_item.description = description
                                variant_item.preview = preview
                            else:
                                variant_item = api_models.VariantItem.objects.create(
                                    variant=existing_variant,
                                    title=title,
                                    description=description,
                                    preview=preview
                                )
                        
                        variant_item.save()

                else:
                    new_variant = api_models.Variant.objects.create(
                        course=course, title=title
                    )

                    for item_data in item_data_list:
                        preview_value = item_data.get("preview")
                        preview = bool(strtobool(str(preview_value))) if preview_value is not None else False

                        api_models.VariantItem.objects.create(
                            variant=new_variant,
                            title=item_data.get("title"),
                            description=item_data.get("description"),
                            file=item_data.get("file"),
                            preview=preview,
                        )

    def save_nested_data(self, course_instance, serializer_class, data):
        serializer = serializer_class(data=data, many=True, context={"course_instance": course_instance})
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course_instance) 

class CourseDetailAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        slug = self.kwargs['slug']
        return api_models.Course.objects.get(slug=slug)

class CourseVariantDeleteAPIView(generics.DestroyAPIView):
    serializer_class = api_serializer.VariantSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        variant_id = self.kwargs['variant_id']
        teacher_id = self.kwargs['teacher_id']
        course_id = self.kwargs['course_id']

        print("variant_id ========", variant_id)

        teacher = api_models.Teacher.objects.get(id=teacher_id)
        course = api_models.Course.objects.get(teacher=teacher, course_id=course_id)
        return api_models.Variant.objects.get(id=variant_id)
    
class CourseVariantItemDeleteAPIVIew(generics.DestroyAPIView):

    serializer_class = api_serializer.VariantItemSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        variant_id = self.kwargs['variant_id']
        variant_item_id = self.kwargs['variant_item_id']
        teacher_id = self.kwargs['teacher_id']
        course_id = self.kwargs['course_id']


        teacher = api_models.Teacher.objects.get(id=teacher_id)
        course = api_models.Course.objects.get(teacher=teacher, course_id=course_id)
        variant = api_models.Variant.objects.get(variant_id=variant_id, course=course)
        return api_models.VariantItem.objects.get(variant=variant, variant_item_id=variant_item_id)
    

class FileUploadAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser,)  # Allow file uploads

    @swagger_auto_schema(
        operation_description="Upload a file",
        request_body=api_serializer.FileUploadSerializer,  # Use the serializer here
        responses={
            200: openapi.Response('File uploaded successfully', openapi.Schema(type=openapi.TYPE_OBJECT)),
            400: openapi.Response('No file provided', openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )

    def post(self, request):
        
        serializer = api_serializer.FileUploadSerializer(data=request.data)  

        if serializer.is_valid():
            file = serializer.validated_data.get("file")

            # Create a compact filename: 8-char id + original extension
            orig_ext = os.path.splitext(file.name)[1]
            compact_name = f"{uuid.uuid4().hex[:8]}{orig_ext}"

            # Save the file to the media directory using compact name
            file_path = default_storage.save(compact_name, ContentFile(file.read()))
            file_url = request.build_absolute_uri(default_storage.url(file_path))

            # Check if the file is a video by inspecting its extension
            if file.name.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                # Calculate the video duration
                try:
                    file_full_path = default_storage.path(file_path)
                except Exception:
                    # Fallback for storages without .path; best-effort join
                    file_full_path = os.path.join(getattr(default_storage, 'location', ''), file_path)
                clip = VideoFileClip(file_full_path)
                duration_seconds = clip.duration

                # Calculate minutes and seconds
                minutes, remainder = divmod(duration_seconds, 60)
                minutes = math.floor(minutes)
                seconds = math.floor(remainder)

                duration_text = f"{minutes}m {seconds}s"

                print("url ==========", file_url)
                print("duration_seconds ==========", duration_seconds)

                # Return both the file URL and the video duration
                return Response({
                    "url": file_url,
                    "video_duration": duration_text
                })

            # If not a video, just return the file URL
            return Response({
                    "url": file_url,
            })

        return Response({"error": "No file provided"}, status=400)



'''

EXPERIMENTAL

'''


class StudentCertificateCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CertificateSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        course_id = request.data.get('course_id')
        
        # Get the user and course
        try:
            user = User.objects.get(id=user_id)
            course = api_models.Course.objects.get(course_id=course_id)
        except (User.DoesNotExist, api_models.Course.DoesNotExist):
            return Response(
                {"message": "User or course not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if the student is enrolled in the course
        enrollment = api_models.EnrolledCourse.objects.filter(
            user=user, 
            course=course
        ).first()
        
        if not enrollment:
            return Response(
                {"message": "You are not enrolled in this course"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if certificate already exists
        certificate = api_models.Certificate.objects.filter(
            user=user, 
            course=course
        ).first()
        
        if certificate:
            # Return the existing certificate
            serializer = self.get_serializer(certificate)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Check if the course is completed
        total_lectures = course.get_total_lectures()
        completed_lessons = api_models.CompletedLesson.objects.filter(
            user=user,
            course=course
        ).count()
        
        completion_percentage = (completed_lessons / total_lectures * 100) if total_lectures > 0 else 0
        
        # Only create certificate if all lessons are completed
        if completed_lessons >= total_lectures:
            # Create certificate with the new model fields
            certificate_data = {
                'user': user.id,
                'course': course.id,
                'student_name': user.full_name or user.username,
                'course_name': course.title,
                'completion_date': timezone.now().date(),
                'status': 'active',
            }
            
            serializer = self.get_serializer(data=certificate_data)
            serializer.is_valid(raise_exception=True)
            certificate = self.perform_create(serializer)
            
            # Generate verification URL for the certificate
            if certificate and hasattr(certificate, 'generate_verification_url'):
                certificate.generate_verification_url()
            
            # Create notification for student
            api_models.Notification.objects.create(
                user=user,
                teacher=course.teacher,
                type="Course Enrollment Completed",
                seen=False
            )
            
            # Create notification for teacher
            api_models.Notification.objects.create(
                teacher=course.teacher,
                type="Course Enrollment Completed",
                seen=False
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {
                    "message": "Course not fully completed. Complete all lessons to get a certificate.",
                    "completed_lessons": completed_lessons,
                    "total_lectures": total_lectures,
                    "completion_percentage": completion_percentage
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def perform_create(self, serializer):
        return serializer.save()

class StudentCertificateListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CertificateSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        return api_models.Certificate.objects.filter(user=user)

class StudentCertificateDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CertificateSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        certificate_id = self.kwargs['certificate_id']
        user_id = self.kwargs['user_id']
        
        try:
            user = User.objects.get(id=user_id)
            return api_models.Certificate.objects.get(
                certificate_id=certificate_id,
                user=user
            )
        except api_models.Certificate.DoesNotExist:
            return None

class CertificateVerificationAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CertificateSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        certificate_id = self.kwargs.get('certificate_id')
        
        try:
            certificate = api_models.Certificate.objects.get(
                certificate_id=certificate_id
            )
            return certificate
        except api_models.Certificate.DoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({
                "verified": False,
                "message": "Certificate verification failed. This certificate is either invalid or has been revoked."
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if certificate is active
        if instance.status != 'active':
            return Response({
                "verified": False,
                "message": f"Certificate is {instance.status}.",
                "status": instance.status
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(instance)
        data = serializer.data
        data.update({
            "verified": True,
            "message": "Certificate successfully verified."
        })
        return Response(data)


class NFTMintAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.NFTSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # Extract data from request, handling both camelCase and snake_case
        enrollment_id = request.data.get('enrollment_id') or request.data.get('enrollmentId')
        policy_id = request.data.get('policy_id') or request.data.get('policyId')
        asset_id = request.data.get('asset_id') or request.data.get('assetId')
        asset_name = request.data.get('asset_name') or request.data.get('assetName')
        tx_hash = request.data.get('tx_hash') or request.data.get('txHash')
        image = request.data.get('image')

        # Check each required field and collect missing ones
        missing_fields = []
        if not enrollment_id:
            missing_fields.append('enrollment_id')
        if not policy_id:
            missing_fields.append('policy_id')
        if not asset_id:
            missing_fields.append('asset_id')
        if not asset_name:
            missing_fields.append('asset_name')
        if not tx_hash:
            missing_fields.append('tx_hash')
        if not image:
            missing_fields.append('image')

        if missing_fields:
            return Response(
                {
                    "error": "Missing required fields",
                    "missing_fields": missing_fields,
                    "required_fields": {
                        "enrollment_id": "ID of the enrollment",
                        "policy_id": "Cardano policy ID",
                        "asset_id": "Unique asset ID",
                        "asset_name": "Name of the NFT",
                        "tx_hash": "Transaction hash",
                        "image": "URL of the NFT image"
                    },
                    "note": "You can use either snake_case (enrollment_id) or camelCase (enrollmentId) for field names"
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get enrollment object
        try:
            enrollment = api_models.EnrolledCourse.objects.get(enrollment_id=enrollment_id)
        except api_models.EnrolledCourse.DoesNotExist:
            return Response(
                {"error": "Enrollment not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if NFT already exists
        if api_models.NFT.objects.filter(asset_id=asset_id).exists():
            return Response(
                {"error": "NFT with this asset ID already exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create NFT
        nft_data = {
            'enrollment': enrollment.id,
            'policy_id': policy_id,
            'asset_id': asset_id,
            'asset_name': asset_name,
            'tx_hash': tx_hash,
            'image': image
        }

        serializer = self.get_serializer(data=nft_data)
        serializer.is_valid(raise_exception=True)
        nft = self.perform_create(serializer)

        # Create notification for user
        api_models.Notification.objects.create(
            user=enrollment.user,
            teacher=enrollment.teacher,
            type="Course NFT Minted",
            seen=False
        )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class NFTAssetIdByEnrollmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, enrollment_id):
        nft = api_models.NFT.objects.filter(enrollment__enrollment_id=enrollment_id).first()
        if not nft:
            return Response({"error": "NFT not found for this enrollment_id"}, status=status.HTTP_404_NOT_FOUND)
        # Check if the requesting user is the owner of the enrollment
        if not nft.enrollment.user or nft.enrollment.user.id != request.user.id:
            return Response({"error": "You are not authorized to access this NFT asset_id."}, status=status.HTTP_403_FORBIDDEN)
        return Response({"asset_id": nft.asset_id}, status=status.HTTP_200_OK)

class MINTCertificateNFTAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CertificateNFTSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        certificate_id = request.data.get('certificate_id') or request.data.get('certificateId')
        policy_id = request.data.get('policy_id') or request.data.get('policyId')
        asset_id = request.data.get('asset_id') or request.data.get('assetId')
        asset_name = request.data.get('asset_name') or request.data.get('assetName')
        tx_hash = request.data.get('tx_hash') or request.data.get('txHash')
        image = request.data.get('image')

        missing_fields = []
        if not certificate_id:
            missing_fields.append('certificate_id')
        if not policy_id:
            missing_fields.append('policy_id')
        if not asset_id:
            missing_fields.append('asset_id')
        if not asset_name:
            missing_fields.append('asset_name')
        if not tx_hash:
            missing_fields.append('tx_hash')
        if not image:
            missing_fields.append('image')

        if missing_fields:
            return Response(
                {
                    "error": "Missing required fields",
                    "missing_fields": missing_fields,
                    "required_fields": {
                        "certificate_id": "ID of the certificate",
                        "policy_id": "Cardano policy ID",
                        "asset_id": "Unique asset ID",
                        "asset_name": "Name of the NFT",
                        "tx_hash": "Transaction hash",
                        "image": "URL of the NFT image"
                    },
                    "note": "You can use either snake_case (certificate_id) or camelCase (certificateId) for field names"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get certificate object
        try:
            certificate = api_models.Certificate.objects.get(certificate_id=certificate_id)
        except api_models.Certificate.DoesNotExist:
            return Response(
                {"error": "Certificate not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if CertificateNFT already exists
        if api_models.CertificateNFT.objects.filter(asset_id=asset_id).exists():
            return Response(
                {"error": "Certificate NFT with this asset ID already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        nft_data = {
            'certificate': certificate.id,
            'policy_id': policy_id,
            'asset_id': asset_id,
            'asset_name': asset_name,
            'tx_hash': tx_hash,
            'image': image
        }

        serializer = self.get_serializer(data=nft_data)
        serializer.is_valid(raise_exception=True)
        nft = self.perform_create(serializer)

        # Create notification for user
        api_models.Notification.objects.create(
            user=certificate.user,
            teacher=certificate.course.teacher,
            type="Certificate NFT Minted",
            seen=False
        )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class CertificateNFTByCertificateAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CertificateNFTSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        certificate_id = self.kwargs.get('certificate_id')
        try:
            certificate = api_models.Certificate.objects.get(certificate_id=certificate_id)
            return api_models.CertificateNFT.objects.get(certificate=certificate)
        except (api_models.Certificate.DoesNotExist, api_models.CertificateNFT.DoesNotExist):
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({
                "verified": False,
                "message": "Certificate NFT not found for this certificate_id."
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if the underlying certificate is active
        certificate = instance.certificate
        if certificate.status != 'active':
            return Response({
                "verified": False,
                "message": f"Certificate is {certificate.status}.",
                "status": certificate.status
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance)
        data = serializer.data
        data.update({
            "verified": True,
            "message": "Certificate NFT successfully verified."
        })
        return Response(data, status=status.HTTP_200_OK)

# ===================== QUIZ API VIEWS =====================

class QuizCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.QuizSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        title = request.data.get('title')
        description = request.data.get('description', '')
        time_limit = request.data.get('time_limit')
        shuffle_questions = request.data.get('shuffle_questions', True)
        min_pass_points = request.data.get('min_pass_points', 0)
        max_attempts = request.data.get('max_attempts', 1)

        course = api_models.Course.objects.filter(course_id=course_id).first()
        if not course:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        if hasattr(course, 'quiz'):
            return Response({'error': 'Quiz already exists for this course'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            teacher = api_models.Teacher.objects.get(user=request.user)
        except api_models.Teacher.DoesNotExist:
            return Response({'error': 'Teacher profile not found.'}, status=status.HTTP_400_BAD_REQUEST)

        quiz = api_models.Quiz.objects.create(
            course=course,
            teacher=teacher,
            title=title,
            description=description,
            time_limit=time_limit,
            shuffle_questions=shuffle_questions,
            min_pass_points=min_pass_points,
            max_attempts=max_attempts
        )
        serializer = self.get_serializer(quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class QuizDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.QuizSerializer
    permission_classes = [AllowAny]
    lookup_field = 'quiz_id'

    def get_object(self):
        quiz_id = self.kwargs['quiz_id']
        return api_models.Quiz.objects.get(quiz_id=quiz_id)

class QuizQuestionCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.QuizQuestionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        quiz_id = request.data.get('quiz_id')
        question_text = request.data.get('question_text')
        points = request.data.get('points', 1)
        order = request.data.get('order', 0)
        options = request.data.get('options', [])

        quiz = api_models.Quiz.objects.filter(quiz_id=quiz_id).first()
        if not quiz:
            return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)

        question = api_models.QuizQuestion.objects.create(
            quiz=quiz,
            question_text=question_text,
            points=points,
            order=order
        )
        for opt in options:
            api_models.QuizQuestionOption.objects.create(
                question=question,
                option_text=opt.get('option_text'),
                is_correct=opt.get('is_correct', False)
            )
        serializer = self.get_serializer(question)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class QuizAttemptCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.QuizAttemptSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        quiz_id = request.data.get('quiz_id')
        answers = request.data.get('answers', [])  # [{question_id, selected_option_id}]
        quiz = api_models.Quiz.objects.filter(quiz_id=quiz_id).first()
        if not quiz:
            return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        attempt_count = api_models.QuizAttempt.objects.filter(quiz=quiz, user=user).count()
        if attempt_count >= quiz.max_attempts:
            return Response({'error': 'Maximum attempts reached'}, status=status.HTTP_400_BAD_REQUEST)
        attempt_number = attempt_count + 1
        attempt = api_models.QuizAttempt.objects.create(quiz=quiz, user=user, attempt_number=attempt_number)
        score = 0
        for ans in answers:
            question = api_models.QuizQuestion.objects.filter(quiz_question_id=ans.get('question_id')).first()
            selected_option = api_models.QuizQuestionOption.objects.filter(quiz_question_option_id=ans.get('selected_option_id')).first()
            is_correct = selected_option.is_correct if selected_option and selected_option.is_correct else False
            if is_correct:
                score += question.points
            api_models.QuizAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_option,
                is_correct=is_correct
            )
        attempt.score = score
        attempt.save()
        serializer = self.get_serializer(attempt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class QuizAttemptListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.QuizAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_id')
        user = self.request.user
        quiz = api_models.Quiz.objects.filter(quiz_id=quiz_id).first()
        if not quiz:
            return api_models.QuizAttempt.objects.none()
        return api_models.QuizAttempt.objects.filter(quiz=quiz, user=user)

class QuizUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = api_serializer.QuizSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'quiz_id'

    def get_object(self):
        quiz_id = self.kwargs['quiz_id']
        return api_models.Quiz.objects.get(quiz_id=quiz_id)

class QuizDeleteAPIView(generics.DestroyAPIView):
    serializer_class = api_serializer.QuizSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'quiz_id'

    def get_object(self):
        quiz_id = self.kwargs['quiz_id']
        return api_models.Quiz.objects.get(quiz_id=quiz_id)

class QuizListByCourseAPIView(generics.ListAPIView):
    serializer_class = api_serializer.QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = api_models.Course.objects.filter(course_id=course_id).first()
        if not course:
            return api_models.Quiz.objects.none()
        return api_models.Quiz.objects.filter(course=course)

class QuizQuestionUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = api_serializer.QuizQuestionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'quiz_question_id'

    def get_object(self):
        quiz_question_id = self.kwargs['quiz_question_id']
        return api_models.QuizQuestion.objects.get(quiz_question_id=quiz_question_id)

class QuizQuestionDeleteAPIView(generics.DestroyAPIView):
    serializer_class = api_serializer.QuizQuestionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'quiz_question_id'

    def get_object(self):
        quiz_question_id = self.kwargs['quiz_question_id']
        return api_models.QuizQuestion.objects.get(quiz_question_id=quiz_question_id)

class QuizQuestionListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.QuizQuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        quiz_id = self.kwargs['quiz_id']
        quiz = api_models.Quiz.objects.filter(quiz_id=quiz_id).first()
        if not quiz:
            return api_models.QuizQuestion.objects.none()
        return api_models.QuizQuestion.objects.filter(quiz=quiz)

class TakeQuizAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = api_serializer.QuizSerializer
    lookup_field = 'quiz_id'

    def get_object(self):
        quiz_id = self.kwargs['quiz_id']
        return api_models.Quiz.objects.get(quiz_id=quiz_id)

    def retrieve(self, request, *args, **kwargs):
        quiz = self.get_object()
        # Hide correct answers in options
        data = self.get_serializer(quiz).data
        for q in data['questions']:
            for opt in q['options']:
                if 'is_correct' in opt:
                    opt.pop('is_correct')
        return Response(data)

class QuizBestAttemptAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = api_serializer.QuizAttemptSerializer
    lookup_field = 'quiz_id'

    def get_object(self):
        quiz_id = self.kwargs['quiz_id']
        quiz = api_models.Quiz.objects.get(quiz_id=quiz_id)
        user = self.request.user
        best = api_models.QuizAttempt.objects.filter(quiz=quiz, user=user).order_by('-score').first()
        if not best:
            raise api_models.QuizAttempt.DoesNotExist()
        return best

class QuizAnalyticsAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = api_serializer.QuizAttemptSerializer  # Add this line
    
    def get(self, request, quiz_id):
        quiz = api_models.Quiz.objects.get(quiz_id=quiz_id)
        attempts = api_models.QuizAttempt.objects.filter(quiz=quiz)
        total_students = attempts.values('user').distinct().count()
        avg_score = attempts.aggregate(models.Avg('score'))['score__avg'] or 0
        pass_count = attempts.filter(score__gte=quiz.min_pass_points).values('user').distinct().count()
        pass_rate = (pass_count / total_students * 100) if total_students else 0
        highest = attempts.aggregate(models.Max('score'))['score__max'] or 0
        lowest = attempts.aggregate(models.Min('score'))['score__min'] or 0
        attempt_dist = attempts.values('user').annotate(num=models.Count('id')).values_list('num', flat=True)

        # Best attempt per student
        from django.db.models import Max
        best_attempts = attempts.values('user').annotate(
            best_score=Max('score')
        )
        # Get the actual best attempt object for each student
        best_attempt_objs = []
        for ba in best_attempts:
            best = attempts.filter(user=ba['user'], score=ba['best_score']).order_by('-score', 'completed_at').first()
            if best:
                best_attempt_objs.append(best)
        # Sort by score descending
        best_attempt_objs = sorted(best_attempt_objs, key=lambda x: x.score, reverse=True)
        # Top performers: top 5 best attempts
        top_performers = best_attempt_objs[:5]
        # All students' best attempts
        students_best = [
            {
                'user_id': a.user.id,
                'score': a.score,
                'attempt_number': a.attempt_number,
                'completed_at': a.completed_at
            } for a in best_attempt_objs
        ]
        return Response({
            'total_students': total_students,
            'avg_score': avg_score,
            'pass_rate': pass_rate,
            'highest_score': highest,
            'lowest_score': lowest,
            'attempts_distribution': list(attempt_dist),
            'top_performers': [
                {
                    'user_id': a.user.id,
                    'score': a.score,
                    'attempt_number': a.attempt_number,
                    'completed_at': a.completed_at
                } for a in top_performers
            ],
            'students_best_attempts': students_best
        })

class QuizAttemptResultAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = api_serializer.QuizAttemptSerializer
    lookup_field = 'attempt_id'

    def get_object(self):
        attempt_id = self.kwargs['attempt_id']
        return api_models.QuizAttempt.objects.get(attempt_id=attempt_id, user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        attempt = self.get_object()
        quiz = attempt.quiz
        
        # Calculate pass/fail status
        passed = attempt.score >= quiz.min_pass_points
        
        # Get detailed answer breakdown
        answers_detail = []
        for answer in attempt.answers.all():
            answers_detail.append({
                'question_id': answer.question.quiz_question_id,
                'question_text': answer.question.question_text,
                'selected_option_id': answer.selected_option.quiz_question_option_id if answer.selected_option else None,
                'selected_option_text': answer.selected_option.option_text if answer.selected_option else None,
                'is_correct': answer.is_correct,
                'points_earned': answer.question.points if answer.is_correct else 0,
                'points_possible': answer.question.points
            })
        
        # Calculate total possible points
        total_possible = sum(answer['points_possible'] for answer in answers_detail)
        
        result_data = {
            'attempt_id': attempt.attempt_id,
            'quiz_id': quiz.quiz_id,
            'quiz_title': quiz.title,
            'score': attempt.score,
            'total_possible': total_possible,
            'percentage': round((attempt.score / total_possible * 100), 2) if total_possible > 0 else 0,
            'passed': passed,
            'min_pass_points': quiz.min_pass_points,
            'attempt_number': attempt.attempt_number,
            'completed_at': attempt.completed_at,
            'answers_breakdown': answers_detail,
            'summary': {
                'total_questions': len(answers_detail),
                'correct_answers': sum(1 for answer in answers_detail if answer['is_correct']),
                'incorrect_answers': sum(1 for answer in answers_detail if not answer['is_correct']),
                'unanswered': sum(1 for answer in answers_detail if answer['selected_option_id'] is None)
            }
        }
        
        return Response(result_data)

class QuizStudentStatusAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = api_serializer.QuizAttemptSerializer  # Add this line
    
    def get(self, request, quiz_id):
        try:
            quiz = api_models.Quiz.objects.get(quiz_id=quiz_id)
            user = request.user
            
            # Get all attempts for this student and quiz
            attempts = api_models.QuizAttempt.objects.filter(quiz=quiz, user=user)
            
            if not attempts.exists():
                return Response({
                    'quiz_id': quiz_id,
                    'quiz_title': quiz.title,
                    'has_attempted': False,
                    'total_attempts': 0,
                    'best_score': 0,
                    'passed': False,
                    'attempts_remaining': quiz.max_attempts,
                    'min_pass_points': quiz.min_pass_points
                })
            
            # Calculate best score
            best_attempt = attempts.order_by('-score').first()
            best_score = best_attempt.score
            
            # Check if passed (any attempt with score >= min_pass_points)
            passed = attempts.filter(score__gte=quiz.min_pass_points).exists()
            
            # Calculate attempts remaining
            total_attempts = attempts.count()
            attempts_remaining = max(0, quiz.max_attempts - total_attempts)
            
            return Response({
                'quiz_id': quiz_id,
                'quiz_title': quiz.title,
                'has_attempted': True,
                'total_attempts': total_attempts,
                'best_score': best_score,
                'passed': passed,
                'attempts_remaining': attempts_remaining,
                'min_pass_points': quiz.min_pass_points,
                'max_attempts': quiz.max_attempts
            })
            
        except api_models.Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

