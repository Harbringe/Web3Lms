from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError


from userauths.models import User, Profile
from shortuuid.django_fields import ShortUUIDField
from .utils import (
    course_image_upload_path,
    course_video_upload_path,
    course_file_upload_path,
    teacher_image_upload_path,
    category_image_upload_path,
)
# from moviepy.editor import VideoFileClip
import math

LANGUAGE = (
    ("English", "English"),
    ("Spanish", "Spanish"),
    ("French", "French"),
)

LEVEL = (
    ("Beginner", "Beginner"),
    ("Intemediate", "Intemediate"),
    ("Advanced", "Advanced"),
)


TEACHER_STATUS = (
    ("Draft", "Draft"),
    ("Disabled", "Disabled"),
    ("Published", "Published"),
)

PAYMENT_STATUS = (
    ("Paid", "Paid"),
    ("Processing", "Processing"),
    ("Failed", "Failed"),
)


PLATFORM_STATUS = (
    ("Review", "Review"),
    ("Disabled", "Disabled"),
    ("Rejected", "Rejected"),
    ("Draft", "Draft"),
    ("Published", "Published"),
)

RATING = (
    (1, "1 Star"),
    (2, "2 Star"),
    (3, "3 Star"),
    (4, "4 Star"),
    (5, "5 Star"),
)

NOTI_TYPE = (
    ("New Order", "New Order"),
    ("New Review", "New Review"),
    ("New Course Question", "New Course Question"),
    ("Draft", "Draft"),
    ("Course Published", "Course Published"),
    ("Course Enrollment Completed", "Course Enrollment Completed"),
)

# In your model or view
default_avatar = settings.DEFAULT_AVATAR

# In your model or view
default_course_image = settings.DEFAULT_COURSE_IMAGE

# In your model or view
default_category_image = settings.DEFAULT_CATEGORY_IMAGE

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.FileField(upload_to=teacher_image_upload_path, blank=True, null=True, default=default_avatar)
    full_name = models.CharField(max_length=100)
    bio = models.CharField(max_length=100, null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    # wallet_address = models.CharField(max_length=1000, unique=True, blank=True, null=True)

    def __str__(self):
        return self.full_name
    
    def students(self):
        return CartOrderItem.objects.filter(teacher=self)
    
    def courses(self):
        return Course.objects.filter(teacher=self)
    
    def review(self):
        return Course.objects.filter(teacher=self).count()
    
    @property
    def image_url(self):
        """Get the proper image URL for Cloudinary or local storage"""
        if self.image:
            # If using Cloudinary, return the URL directly
            if hasattr(self.image, 'url'):
                return self.image.url
            # Fallback for local storage
            return f'/media/{self.image}'
        return None
    
    def get_image_url_safe(self):
        """
        Safe method to get image URL that handles both old and new paths
        """
        if not self.image:
            return None
            
        try:
            # Try to get the URL normally first
            if hasattr(self.image, 'url'):
                return self.image.url
        except Exception:
            pass
        
        # Fallback: construct URL manually
        image_path = str(self.image)
        
        # Handle Cloudinary URLs
        if 'cloudinary.com' in image_path:
            return image_path
        
        # Handle local storage URLs
        if image_path.startswith('/'):
            return image_path
        else:
            return f'/media/{image_path}'
    
    # def save(self, *args, **kwargs):
    #     if not self.wallet_address:
    #         self.wallet_address = self.user.wallet_address
    #     super().save(*args, **kwargs)
    
class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.FileField(upload_to=category_image_upload_path, default=default_category_image, null=True, blank=True)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Category"
        ordering = ['title']

    def __str__(self):
        return self.title
    
    def course_count(self):
        return Course.objects.filter(category=self).count()
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) 
        super(Category, self).save(*args, **kwargs)
    
    @property
    def image_url(self):
        """Get the proper image URL for Cloudinary or local storage"""
        if self.image:
            # If using Cloudinary, return the URL directly
            if hasattr(self.image, 'url'):
                return self.image.url
            # Fallback for local storage
            return f'/media/{self.image}'
        return None
    
    def get_image_url_safe(self):
        """
        Safe method to get image URL that handles both old and new paths
        """
        if not self.image:
            return None
            
        try:
            # Try to get the URL normally first
            if hasattr(self.image, 'url'):
                return self.image.url
        except Exception:
            pass
        
        # Fallback: construct URL manually
        image_path = str(self.image)
        
        # Handle Cloudinary URLs
        if 'cloudinary.com' in image_path:
            return image_path
        
        # Handle local storage URLs
        if image_path.startswith('/'):
            return image_path
        else:
            return f'/media/{image_path}'
            

class Course(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to=course_video_upload_path, blank=True, null=True, default=default_course_image)
    image = models.FileField(upload_to=course_image_upload_path, blank=True, null=True, default=default_course_image)
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    language = models.CharField(choices=LANGUAGE, default="English", max_length=100, blank=True, null=True)
    level = models.CharField(choices=LEVEL, default="Beginner", max_length=100, blank=True, null=True)
    platform_status = models.CharField(choices=PLATFORM_STATUS, default="Published", max_length=100, blank=True, null=True)
    teacher_course_status = models.CharField(choices=TEACHER_STATUS, default="Published", max_length=100)
    featured = models.BooleanField(default=False)
    course_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890", null=False, blank=False)
    slug = models.SlugField(unique=True, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Course"
        verbose_name_plural = "Courses"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "_" + str(self.course_id)
            
        super(Course, self).save(*args, **kwargs)

    def students(self):        
        return EnrolledCourse.objects.filter(course=self)
    
    def curriculum(self):
        return Variant.objects.filter(course=self)
    
    def lectures(self):
        return VariantItem.objects.filter(variant__course=self)
    
    def average_rating(self):
        average_rating = Review.objects.filter(course=self, active=True).aggregate(avg_rating=models.Avg('rating'))
        return average_rating['avg_rating'] 
    
    def rating_count(self):
        return Review.objects.filter(course=self, active=True).count()
    
    def reviews(self):
        return Review.objects.filter(course=self, active=True)

    def is_published(self):
        return self.platform_status == "Published" and self.teacher_course_status == "Published"
    
    def get_total_duration(self):
        total_seconds = 0
        for variant in self.curriculum():
            for item in variant.variant_items.all():
                if item.duration:
                    total_seconds += item.duration.total_seconds()
        
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
    
    def get_total_lectures(self):
        return self.lectures().count()
    
    @property
    def image_url(self):
        """Get the proper image URL for Cloudinary or local storage"""
        if self.image:
            # If using Cloudinary, return the URL directly
            if hasattr(self.image, 'url'):
                return self.image.url
            # Fallback for local storage
            return f'/media/{self.image}'
        return None
    
    @property
    def file_url(self):
        """Get the proper file URL for Cloudinary or local storage"""
        if self.file:
            # If using Cloudinary, return the URL directly
            if hasattr(self.file, 'url'):
                return self.file.url
            # Fallback for local storage
            return f'/media/{self.file}'
        return None
    
    def get_image_url_safe(self):
        """
        Safe method to get image URL that handles both old and new paths
        """
        if not self.image:
            return None
            
        try:
            # Try to get the URL normally first
            if hasattr(self.image, 'url'):
                return self.image.url
        except Exception:
            pass
        
        # Fallback: construct URL manually
        image_path = str(self.image)
        
        # Handle Cloudinary URLs
        if 'cloudinary.com' in image_path:
            return image_path
        
        # Handle local storage URLs
        if image_path.startswith('/'):
            return image_path
        else:
            return f'/media/{image_path}'
    
    def get_file_url_safe(self):
        """
        Safe method to get file URL that handles both old and new paths
        """
        if not self.file:
            return None
            
        try:
            # Try to get the URL normally first
            if hasattr(self.file, 'url'):
                return self.file.url
        except Exception:
            pass
        
        # Fallback: construct URL manually
        file_path = str(self.file)
        
        # Handle Cloudinary URLs
        if 'cloudinary.com' in file_path:
            return file_path
        
        # Handle local storage URLs
        if file_path.startswith('/'):
            return file_path
        else:
            return f'/media/{file_path}'


class Certificate(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    certificate_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    student_name = models.CharField(max_length=200)
    course_name = models.CharField(max_length=200)
    completion_date = models.DateField()
    issue_date = models.DateTimeField(auto_now_add=True)
    verification_url = models.URLField(blank=True, null=True)
    status = models.CharField(
        choices=[
            ('active', 'Active'),
            ('revoked', 'Revoked'),
            ('expired', 'Expired')
        ],
        default='active',
        max_length=20
    )
    pdf_file = models.FileField(upload_to=course_file_upload_path, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)  # For storing additional certificate data

    def __str__(self):
        return f"{self.student_name} - {self.course_name}"
    
    @property
    def pdf_url(self):
        """Get the proper PDF URL for Cloudinary or local storage"""
        if self.pdf_file:
            # If using Cloudinary, return the URL directly
            if hasattr(self.pdf_file, 'url'):
                return self.pdf_file.url
            # Fallback for local storage
            return f'/media/{self.pdf_file}'
        return None
    
    def get_pdf_url_safe(self):
        """
        Safe method to get PDF URL that handles both old and new paths
        """
        if not self.pdf_file:
            return None
            
        try:
            # Try to get the URL normally first
            if hasattr(self.pdf_file, 'url'):
                return self.pdf_file.url
        except Exception:
            pass
        
        # Fallback: construct URL manually
        file_path = str(self.pdf_file)
        
        # Handle Cloudinary URLs
        if 'cloudinary.com' in file_path:
            return file_path
        
        # Handle local storage URLs
        if file_path.startswith('/'):
            return file_path
        else:
            return f'/media/{file_path}'
    
    def save(self, *args, **kwargs):
        if not self.student_name and self.user:
            self.student_name = self.user.full_name or self.user.username
        if not self.course_name and self.course:
            self.course_name = self.course.title
        if not self.completion_date:
            self.completion_date = timezone.now().date()
        super().save(*args, **kwargs)

    def generate_verification_url(self):
        """Generate a unique verification URL for the certificate"""
        if not self.verification_url:
            self.verification_url = f"{settings.FRONTEND_SITE_URL}/verify-certificate/{self.certificate_id}"
            self.save()
        return self.verification_url

    def revoke(self):
        """Revoke the certificate"""
        self.status = 'revoked'
        self.save()

    def verify(self):
        """Verify if the certificate is valid"""
        return self.status == 'active'

    class Meta:
        ordering = ['-issue_date']
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"



class Variant(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    variant_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
    
    def variant_items(self):
        return VariantItem.objects.filter(variant=self)
    
    def items(self):
        return VariantItem.objects.filter(variant=self)
    
    
class VariantItem(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="variant_items")
    title = models.CharField(max_length=1000)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to=course_video_upload_path, blank=True, null=True, default="")
    duration = models.DurationField(null=True, blank=True)
    content_duration = models.CharField(max_length=1000, null=True, blank=True)
    preview = models.BooleanField(default=False)
    variant_item_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.variant.title} - {self.title}"
    
    @property
    def file_url(self):
        """Get the proper file URL for Cloudinary or local storage"""
        if self.file:
            # If using Cloudinary, return the URL directly
            if hasattr(self.file, 'url'):
                return self.file.url
            # Fallback for local storage
            return f'/media/{self.file}'
        return None
    
    def get_file_url_safe(self):
        """
        Safe method to get file URL that handles both old and new paths
        """
        if not self.file:
            return None
            
        try:
            # Try to get the URL normally first
            if hasattr(self.file, 'url'):
                return self.file.url
        except Exception:
            pass
        
        # Fallback: construct URL manually
        file_path = str(self.file)
        
        # Handle Cloudinary URLs
        if 'cloudinary.com' in file_path:
            return file_path
        
        # Handle local storage URLs
        if file_path.startswith('/'):
            return file_path
        else:
            return f'/media/{file_path}'
    
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)

    #     if self.file:
    #         clip = VideoFileClip(self.file.path)
    #         duration_seconds = clip.duration

    #         minutes, remainder = divmod(duration_seconds, 60)  

    #         minutes = math.floor(minutes)
    #         seconds = math.floor(remainder)

    #         duration_text = f"{minutes}m {seconds}s"
    #         self.content_duration = duration_text
    #         super().save(update_fields=['content_duration'])

class Question_Answer(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=1000, null=True, blank=True)
    qa_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    class Meta:
        ordering = ['-date']

    def messages(self):
        return Question_Answer_Message.objects.filter(question=self)
    
    def profile(self):
        return Profile.objects.get(user=self.user)
    
class Question_Answer_Message(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question = models.ForeignKey(Question_Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    qam_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    qa_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    class Meta:
        ordering = ['date']

    def profile(self):
        return Profile.objects.get(user=self.user)
    
class Cart(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    tax_fee = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    total = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    country = models.CharField(max_length=100, null=True, blank=True)
    cart_id = ShortUUIDField(length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title
    
class CartOrder(models.Model):
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    teachers = models.ManyToManyField(Teacher, blank=True)
    sub_total = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    tax_fee = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    total = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    initial_total = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    saved = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    payment_status = models.CharField(choices=PAYMENT_STATUS, default="Processing", max_length=100)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    coupons = models.ManyToManyField("api.Coupon", blank=True)
    # stripe_session_id = models.CharField(max_length=1000, null=True, blank=True)
    oid = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=200, null=True, blank=True)


    class Meta:
        ordering = ['-date']
    
    def order_items(self):
        return CartOrderItem.objects.filter(order=self)
    
    def __str__(self):
        return self.oid
    
class CartOrderItem(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE, related_name="orderitem")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="order_item")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    tax_fee = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    total = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    initial_total = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    saved = models.DecimalField(max_digits=12, default=0.00, decimal_places=2)
    coupons = models.ManyToManyField("api.Coupon", blank=True)
    applied_coupon = models.BooleanField(default=False)
    oid = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date']
    
    def order_id(self):
        return f"Order ID #{self.order.oid}"
    
    def payment_status(self):
        return f"{self.order.payment_status}"
    
    def __str__(self):
        return self.oid
    

        

class CompletedLesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    variant_item = models.ForeignKey(VariantItem, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title
    
class EnrolledCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    order_item = models.ForeignKey(CartOrderItem, on_delete=models.CASCADE)
    enrollment_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title
    
    def lectures(self):
        return VariantItem.objects.filter(variant__course=self.course)
    
    def completed_lesson(self):
        return CompletedLesson.objects.filter(course=self.course, user=self.user)
    
    def curriculum(self):
        return Variant.objects.filter(course=self.course)
    
    def note(self):
        return Note.objects.filter(course=self.course, user=self.user)
    
    def question_answer(self):
        return Question_Answer.objects.filter(course=self.course)
    
    def review(self):
        return Review.objects.filter(course=self.course, user=self.user).first()
    
class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, null=True, blank=True)
    note = models.TextField()
    note_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(default=timezone.now)   

    def __str__(self):
        return self.title
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    reply = models.CharField(null=True, blank=True, max_length=1000)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)   

    def __str__(self):
        return self.course.title
    
    def profile(self):
        return Profile.objects.get(user=self.user)
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(CartOrder, on_delete=models.SET_NULL, null=True, blank=True)
    order_item = models.ForeignKey(CartOrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    review = models.ForeignKey(Review, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=100, choices=NOTI_TYPE)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)  

    def __str__(self):
        return self.type

class Coupon(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    used_by = models.ManyToManyField(User, blank=True)
    code = models.CharField(max_length=50)
    discount = models.IntegerField(default=1)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)   

    def __str__(self):
        return self.code
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.course.title)
    
class Country(models.Model):
    name = models.CharField(max_length=100)
    tax_rate = models.IntegerField(default=5)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class NFT(models.Model):
    enrollment = models.ForeignKey(EnrolledCourse, on_delete=models.CASCADE, related_name='nfts')
    policy_id = models.CharField(max_length=255)
    asset_id = models.CharField(max_length=255, unique=True)
    asset_name = models.CharField(max_length=255)
    tx_hash = models.CharField(max_length=255)
    image = models.URLField()
    minted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Course NFT"
        verbose_name_plural = "Course NFTs"
        ordering = ['-minted_at']

    def __str__(self):
        return f"NFT for {self.enrollment.course.title} - {self.asset_id}"

    @property
    def enrollment_id(self):
        return self.enrollment.enrollment_id if self.enrollment else None

    @property
    def user(self):
        return self.enrollment.user if self.enrollment else None

    def clean(self):
        # Optional: Check if user already owns an NFT for this enrollment
        if NFT.objects.filter(enrollment=self.enrollment).exists():
            raise ValidationError("An NFT already exists for this enrollment")

class CertificateNFT(models.Model):
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='certificate_nfts')
    policy_id = models.CharField(max_length=255)
    asset_id = models.CharField(max_length=255, unique=True)
    asset_name = models.CharField(max_length=255,unique=True)
    tx_hash = models.CharField(max_length=255)
    image = models.URLField()
    minted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Certificate NFT"
        verbose_name_plural = "Certificate NFTs"
        ordering = ['-minted_at']

    def __str__(self):
        return f"Certificate NFT for {self.certificate} - {self.asset_id}"

    @property
    def user(self):
        return self.certificate.user if self.certificate else None

    def clean(self):
        # Optional: Check if a CertificateNFT already exists for this certificate
        if CertificateNFT.objects.filter(certificate=self.certificate).exists():
            raise ValidationError("A Certificate NFT already exists for this certificate")

# ===================== QUIZ MODELS =====================

class Quiz(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name="quiz")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    time_limit = models.PositiveIntegerField(help_text="Time limit in minutes")
    shuffle_questions = models.BooleanField(default=True)
    min_pass_points = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=1)
    quiz_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Quiz for {self.course.title}"

    def total_points(self):
        return sum(q.points for q in self.questions.all())

class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    quiz_question_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")

    def __str__(self):
        return f"{self.question_text} (Quiz: {self.quiz.quiz_id})"

class QuizQuestionOption(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=1000)
    is_correct = models.BooleanField(default=False)
    quiz_question_option_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")

    def __str__(self):
        return f"Option for Q{self.question.quiz_question_id}: {self.option_text}"

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_attempts")
    attempt_number = models.PositiveIntegerField(default=1)
    score = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)
    attempt_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")

    class Meta:
        unique_together = ("quiz", "user", "attempt_number")
        ordering = ["-completed_at"]

    def __str__(self):
        return f"Attempt {self.attempt_number} by {self.user} on {self.quiz.quiz_id}"

class QuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(QuizQuestionOption, on_delete=models.SET_NULL, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    quiz_answer_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")

    def __str__(self):
        return f"Answer to {self.question.quiz_question_id} in Attempt {self.attempt.attempt_id}"