from django.contrib.auth.password_validation import validate_password
from api import models as api_models

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from userauths.models import Profile, User

from api.models import Quiz, QuizQuestion, QuizQuestionOption, QuizAttempt, QuizAnswer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['full_name'] = user.full_name
        token['email'] = user.email
        token['username'] = user.username
        token['wallet_address'] = user.wallet_address
        try:
            token['teacher_id'] = user.teacher.id
        except:
            token['teacher_id'] = 0


        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    wallet_address = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'password2', 'wallet_address']

    def validate(self, attr):
        if attr['password'] != attr['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attr
    
    def create(self, validated_data):
        user = User.objects.create(
            full_name=validated_data['full_name'],
            email=validated_data['email'],
            wallet_address=validated_data['wallet_address']
        )

        email_username, _ = user.email.split("@")
        user.username = email_username
        user.set_password(validated_data['password'])
        user.save()

        return user
    
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['id', 'title', 'image', 'slug', 'course_count']
        model = api_models.Category

class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        fields = [
            "id", 
            "user", 
            "image", 
            "full_name", 
            "bio", 
            "facebook", 
            "twitter", 
            "linkedin", 
            "about", 
            "country",
            "wallet_address",
        ]
        model = api_models.Teacher




class VariantItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        fields = '__all__'
        model = api_models.VariantItem

    
    def __init__(self, *args, **kwargs):
        super(VariantItemSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3


class VariantSerializer(serializers.ModelSerializer):
    variant_items = VariantItemSerializer(many=True)
    items = VariantItemSerializer(many=True)
    class Meta:
        fields = '__all__'
        model = api_models.Variant


    def __init__(self, *args, **kwargs):
        super(VariantSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3




class Question_Answer_MessageSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)

    class Meta:
        fields = '__all__'
        model = api_models.Question_Answer_Message


class Question_AnswerSerializer(serializers.ModelSerializer):
    messages = Question_Answer_MessageSerializer(many=True)
    profile = ProfileSerializer(many=False)
    
    class Meta:
        fields = '__all__'
        model = api_models.Question_Answer



class CartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Cart

    def __init__(self, *args, **kwargs):
        super(CartSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3


class CartOrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.CartOrderItem

    def __init__(self, *args, **kwargs):
        super(CartOrderItemSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3


class CartOrderSerializer(serializers.ModelSerializer):
    order_items = CartOrderItemSerializer(many=True)
    
    class Meta:
        fields = '__all__'
        model = api_models.CartOrder


    def __init__(self, *args, **kwargs):
        super(CartOrderSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3

class CertificateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Certificate



class CompletedLessonSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.CompletedLesson


    def __init__(self, *args, **kwargs):
        super(CompletedLessonSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3

class NoteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Note



class ReviewSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False)

    class Meta:
        fields = '__all__'
        model = api_models.Review

    def __init__(self, *args, **kwargs):
        super(ReviewSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Notification


class CouponSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Coupon


class WishlistSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Wishlist

    def __init__(self, *args, **kwargs):
        super(WishlistSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3

class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = api_models.Country




class EnrolledCourseSerializer(serializers.ModelSerializer):
    lectures = VariantItemSerializer(many=True, read_only=True)
    completed_lesson = CompletedLessonSerializer(many=True, read_only=True)
    curriculum =  VariantSerializer(many=True, read_only=True)
    note = NoteSerializer(many=True, read_only=True)
    question_answer = Question_AnswerSerializer(many=True, read_only=True)
    review = ReviewSerializer(many=False, read_only=True)


    class Meta:
        fields = '__all__'
        model = api_models.EnrolledCourse

    def __init__(self, *args, **kwargs):
        super(EnrolledCourseSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3

class CourseSerializer(serializers.ModelSerializer):
    students = EnrolledCourseSerializer(many=True, required=False, read_only=True,)
    curriculum = VariantSerializer(many=True, required=False, read_only=True,)
    lectures = VariantItemSerializer(many=True, required=False, read_only=True,)
    reviews = ReviewSerializer(many=True, read_only=True, required=False)
    
    class Meta:
        fields = ["id", "category", "teacher", "file", "image", "title", "description", "price", "language", "level", "platform_status", "teacher_course_status", "featured", "course_id", "slug", "date", "students", "curriculum", "lectures", "average_rating", "rating_count", "reviews",]
        model = api_models.Course

    def __init__(self, *args, **kwargs):
        super(CourseSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 3


class StudentSummarySerializer(serializers.Serializer):
    total_courses = serializers.IntegerField(default=0)
    completed_lessons = serializers.IntegerField(default=0)
    achieved_certificates = serializers.IntegerField(default=0)

class TeacherSummarySerializer(serializers.Serializer):
    total_courses = serializers.IntegerField(default=0)
    total_students = serializers.IntegerField(default=0)
    total_revenue = serializers.IntegerField(default=0)
    monthly_revenue = serializers.IntegerField(default=0)




class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)


'''

EXPERIMENTAL

'''

class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    course_image = serializers.SerializerMethodField()
    completion_date = serializers.SerializerMethodField()
    course_level = serializers.SerializerMethodField()
    course_description = serializers.SerializerMethodField()
    
    class Meta:
        fields = [
            'id', 'course', 'user', 'certificate_id', 'student_name', 'course_name',
            'completion_date', 'issue_date', 'verification_url', 'status', 
            'pdf_file', 'metadata', 'course_title', 'teacher_name', 
            'user_name', 'course_image', 'course_level', 'course_description'
        ]
        model = api_models.Certificate
        
    def get_course_title(self, obj):
        return obj.course.title
    
    def get_teacher_name(self, obj):
        if obj.course.teacher:
            return obj.course.teacher.full_name
        return None
    
    def get_user_name(self, obj):
        if obj.user:
            return obj.user.full_name
        return None
    
    def get_course_image(self, obj):
        if obj.course.image:
            return obj.course.image.url
        return None
    
    def get_completion_date(self, obj):
        if hasattr(obj, 'completion_date'):
            return obj.completion_date.strftime("%B %d, %Y")
        return obj.issue_date.strftime("%B %d, %Y")
    
    def get_course_level(self, obj):
        return obj.course.level
    
    def get_course_description(self, obj):
        return obj.course.description
    
    def __init__(self, *args, **kwargs):
        super(CertificateSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1



class NFTSerializer(serializers.ModelSerializer):
    enrollment_id = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = api_models.NFT
        fields = ['id', 'enrollment', 'enrollment_id', 'policy_id', 'asset_id', 
                 'asset_name', 'tx_hash', 'image', 'minted_at', 'user']
        read_only_fields = ['id', 'minted_at', 'enrollment_id', 'user']

    def get_enrollment_id(self, obj):
        return obj.enrollment.enrollment_id if obj.enrollment else None

    def get_user(self, obj):
        return obj.user.id if obj.user else None

    def validate(self, data):
        # Validate enrollment exists
        try:
            enrollment = api_models.EnrolledCourse.objects.get(id=data['enrollment'].id)
        except api_models.EnrolledCourse.DoesNotExist:
            raise serializers.ValidationError("Enrollment does not exist")

        # Validate asset_id is unique
        if api_models.NFT.objects.filter(asset_id=data['asset_id']).exists():
            raise serializers.ValidationError("Asset ID must be unique")

        return data

class CertificateNFTSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    certificate_id = serializers.CharField(source='certificate.certificate_id', read_only=True)

    class Meta:
        model = api_models.CertificateNFT
        fields = ['id', 'certificate', 'certificate_id', 'policy_id', 'asset_id', 'asset_name', 'tx_hash', 'image', 'minted_at', 'user']
        read_only_fields = ['id', 'minted_at', 'user', 'certificate_id']

    def get_user(self, obj):
        return obj.user.id if obj.user else None

# ===================== QUIZ SERIALIZERS =====================

class QuizQuestionOptionSerializer(serializers.ModelSerializer):
    quiz_question_option_id = serializers.CharField(read_only=True)

    class Meta:
        model = QuizQuestionOption
        fields = ['quiz_question_option_id', 'option_text', 'is_correct']

class QuizQuestionSerializer(serializers.ModelSerializer):
    quiz_question_id = serializers.CharField(read_only=True)
    options = QuizQuestionOptionSerializer(many=True)

    class Meta:
        model = QuizQuestion
        fields = ['quiz_question_id', 'question_text', 'points', 'order', 'options']
        read_only_fields = ['quiz_question_id']

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', [])
        # Update the question fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update options
        existing_ids = [opt['quiz_question_option_id'] for opt in options_data if 'quiz_question_option_id' in opt]
        # Delete options not in the payload
        instance.options.exclude(quiz_question_option_id__in=existing_ids).delete()
        for opt_data in options_data:
            opt_id = opt_data.get('quiz_question_option_id', None)
            if opt_id:
                # Update existing option
                option = instance.options.get(quiz_question_option_id=opt_id)
                option.option_text = opt_data.get('option_text', option.option_text)
                option.is_correct = opt_data.get('is_correct', option.is_correct)
                option.save()
            else:
                # Create new option
                QuizQuestionOption.objects.create(
                    question=instance,
                    option_text=opt_data['option_text'],
                    is_correct=opt_data.get('is_correct', False)
                )
        return instance

class QuizSerializer(serializers.ModelSerializer):
    quiz_id = serializers.CharField(read_only=True)
    questions = QuizQuestionSerializer(many=True, read_only=True)
    teacher = serializers.PrimaryKeyRelatedField(read_only=True)
    course_id = serializers.SlugRelatedField(source='course', slug_field='course_id', read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'quiz_id', 'course_id', 'teacher', 'title', 'description', 'time_limit',
            'shuffle_questions', 'min_pass_points', 'max_attempts', 'questions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['quiz_id', 'created_at', 'updated_at', 'course_id']

class QuizAnswerSerializer(serializers.ModelSerializer):
    quiz_answer_id = serializers.CharField(read_only=True)
    question = serializers.PrimaryKeyRelatedField(read_only=True)
    selected_option = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = QuizAnswer
        fields = ['quiz_answer_id', 'attempt', 'question', 'selected_option', 'is_correct']
        read_only_fields = ['quiz_answer_id']

class QuizAttemptSerializer(serializers.ModelSerializer):
    attempt_id = serializers.CharField(read_only=True)
    answers = QuizAnswerSerializer(many=True, read_only=True)
    quiz_id = serializers.SlugRelatedField(source='quiz', slug_field='quiz_id', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['attempt_id', 'quiz_id', 'user', 'attempt_number', 'score', 'completed_at', 'answers']
        read_only_fields = ['attempt_id', 'completed_at', 'quiz_id']