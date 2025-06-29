from api import views as api_views
from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication Endpoints
    path("user/token/", api_views.MyTokenObtainPairView.as_view()),
    path("user/token/refresh/", TokenRefreshView.as_view()),
    path("user/register/", api_views.RegisterView.as_view()),
    path("user/password-reset/<email>/", api_views.PasswordResetEmailVerifyAPIView.as_view()),
    path("user/password-change/", api_views.PasswordChangeAPIView.as_view()),
    path("user/profile/<user_id>/", api_views.ProfileAPIView.as_view()),
    path("user/change-password/", api_views.ChangePasswordAPIView.as_view()),

    # Core Endpoints
    path("course/category/", api_views.CategoryListAPIView.as_view()),
    path("course/course-list/", api_views.CourseListAPIView.as_view()),
    path("course/search/", api_views.SearchCourseAPIView.as_view()),
    path("course/course-detail/<slug>/", api_views.CourseDetailAPIView.as_view()),
    path("course/cart/", api_views.CartAPIView.as_view()),
    path("course/cart-list/<cart_id>/", api_views.CartListAPIView.as_view()),
    path("cart/stats/<cart_id>/", api_views.CartStatsAPIView.as_view()),
    path("course/cart-item-delete/<cart_id>/<item_id>/", api_views.CartItemDeleteAPIView.as_view()),
    path("order/create-order/", api_views.CreateOrderAPIView.as_view()),
    path("order/checkout/<oid>/", api_views.CheckoutAPIView.as_view()),
    path("order/coupon/", api_views.CouponApplyAPIView.as_view()),
    path("payment/razorpay-checkout/<order_oid>/", api_views.RazorpayCheckoutAPIView.as_view()),
    path("payment/payment-success/", api_views.PaymentSuccessAPIView.as_view()),


    # Student API Endpoints
    path("student/summary/<user_id>/", api_views.StudentSummaryAPIView.as_view()),
    path("student/course-list/<user_id>/", api_views.StudentCourseListAPIView.as_view()),
    path("student/course-detail/<user_id>/<enrollment_id>/", api_views.StudentCourseDetailAPIView.as_view()),
    path("student/course-completed/", api_views.StudentCourseCompletedCreateAPIView.as_view()),
    path("student/course-note/<user_id>/<enrollment_id>/", api_views.StudentNoteCreateAPIView.as_view()),
    path("student/course-note-detail/<user_id>/<enrollment_id>/<note_id>/", api_views.StudentNoteDetailAPIView.as_view()),
    path("student/rate-course/", api_views.StudentRateCourseCreateAPIView.as_view()),
    path("student/review-detail/<user_id>/<review_id>/", api_views.StudentRateCourseUpdateAPIView.as_view()),
    path("student/wishlist/<user_id>/", api_views.StudentWishListListCreateAPIView.as_view()),
    path("student/question-answer-list-create/<course_id>/", api_views.QuestionAnswerListCreateAPIView.as_view()),
    path("student/question-answer-message-create/", api_views.QuestionAnswerMessageSendAPIView.as_view()),

    # EXPERIMENTAL

    # Certificate Endpoints
    path("student/certificate/create/", api_views.StudentCertificateCreateAPIView.as_view()),
    path("student/certificate/list/<user_id>/", api_views.StudentCertificateListAPIView.as_view()),
    path("student/certificate/detail/<user_id>/<certificate_id>/", api_views.StudentCertificateDetailAPIView.as_view()),
    path("verify-certificate/<certificate_id>/", api_views.CertificateVerificationAPIView.as_view()),


    # Teacher Routes
    path("teacher/summary/<teacher_id>/", api_views.TeacherSummaryAPIView.as_view()),
    path("teacher/course-lists/<teacher_id>/", api_views.TeacherCourseListAPIView.as_view()),
    path("teacher/review-lists/<teacher_id>/", api_views.TeacherReviewListAPIView.as_view()),
    path("teacher/review-detail/<teacher_id>/<review_id>/", api_views.TeacherReviewDetailAPIView.as_view()),
    path("teacher/student-lists/<teacher_id>/", api_views.TeacherStudentsListAPIVIew.as_view({'get': 'list'})),
    path("teacher/all-months-earning/<teacher_id>/", api_views.TeacherAllMonthEarningAPIView),
    path("teacher/best-course-earning/<teacher_id>/", api_views.TeacherBestSellingCourseAPIView.as_view({'get': 'list'})),
    path("teacher/course-order-list/<teacher_id>/", api_views.TeacherCourseOrdersListAPIView.as_view()),
    path("teacher/question-answer-list/<teacher_id>/", api_views.TeacherQuestionAnswerListAPIView.as_view()),
    path("teacher/coupon-list/<teacher_id>/", api_views.TeacherCouponListCreateAPIView.as_view()),
    path("teacher/coupon-detail/<teacher_id>/<coupon_id>/", api_views.TeacherCouponDetailAPIView.as_view()),
    path("teacher/noti-list/<teacher_id>/", api_views.TeacherNotificationListAPIView.as_view()),
    path("teacher/noti-detail/<teacher_id>/<noti_id>", api_views.TeacherNotificationDetailAPIView.as_view()),
    path("teacher/course-create/", api_views.CourseCreateAPIView.as_view()),
    path("teacher/course-update/<teacher_id>/<course_id>/", api_views.CourseUpdateAPIView.as_view()),
    path("teacher/course-detail/<course_id>/", api_views.TeacherCourseDetailAPIView.as_view()),
    path("teacher/course/variant-delete/<variant_id>/<teacher_id>/<course_id>/", api_views.CourseVariantDeleteAPIView.as_view()),
    path("teacher/course/variant-item-delete/<variant_id>/<variant_item_id>/<teacher_id>/<course_id>/", api_views.CourseVariantItemDeleteAPIVIew.as_view()),

    path("file-upload/", api_views.FileUploadAPIView.as_view()),

    # NFT Endpoints
    # path("nft/", api_views.NFTListCreateAPIView.as_view()),
    # path("nft/<str:policy_id>/", api_views.NFTDetailAPIView.as_view()),
    # path("nft/verify/<str:policy_id>/", api_views.NFTByPolicyIDAPIView.as_view()),
    path("nft/mint/", api_views.NFTMintAPIView.as_view()),
    # path("nft/user/<int:user_id>/", api_views.UserNFTListView.as_view()),
    path("nft/asset-id/<enrollment_id>/", api_views.NFTAssetIdByEnrollmentAPIView.as_view()),

    # Certificate NFT Endpoints
    path("certificate-nft/mint/", api_views.MINTCertificateNFTAPIView.as_view()),
    path("certificate-nft/by-certificate/<certificate_id>/", api_views.CertificateNFTByCertificateAPIView.as_view()),

    # Quiz Endpoints
    path("quiz/create/", api_views.QuizCreateAPIView.as_view()),
    path("quiz/<str:quiz_id>/", api_views.QuizDetailAPIView.as_view()),
    path("quiz/question/create/", api_views.QuizQuestionCreateAPIView.as_view()),
    path("quiz/attempt/create/", api_views.QuizAttemptCreateAPIView.as_view()),
    path("quiz/attempts/<str:quiz_id>/", api_views.QuizAttemptListAPIView.as_view()),
    path("quiz/<str:quiz_id>/update/", api_views.QuizUpdateAPIView.as_view()),
    path("quiz/<str:quiz_id>/delete/", api_views.QuizDeleteAPIView.as_view()),
    path("quiz/course/<str:course_id>/", api_views.QuizListByCourseAPIView.as_view()),
    path("quiz/question/<str:quiz_question_id>/update/", api_views.QuizQuestionUpdateAPIView.as_view()),
    path("quiz/question/<str:quiz_question_id>/delete/", api_views.QuizQuestionDeleteAPIView.as_view()),
    path("quiz/<str:quiz_id>/questions/", api_views.QuizQuestionListAPIView.as_view()),
    path("quiz/<str:quiz_id>/take/", api_views.TakeQuizAPIView.as_view()),
    path("quiz/<str:quiz_id>/best-attempt/", api_views.QuizBestAttemptAPIView.as_view()),
    path("quiz/<str:quiz_id>/analytics/", api_views.QuizAnalyticsAPIView.as_view()),
    path("quiz/attempt/<str:attempt_id>/result/", api_views.QuizAttemptResultAPIView.as_view()),
    path("quiz/<str:quiz_id>/student-status/", api_views.QuizStudentStatusAPIView.as_view()),
]


