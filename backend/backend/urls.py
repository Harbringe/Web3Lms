"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from core.views import health_check

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Knowledge Ledger Backend APIs",
      default_version='v1',
      description="This is the API documentation for Web3 based LMS project APIs",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="aaditya@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   url='https://knowledge-ledger.onrender.com',  
)

urlpatterns = [
    path('swagger<format>/', schema_view.with_ui(cache_timeout=0), name='schema-json'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path("api/v1/", include("api.urls")),
    path("ping/", lambda request: HttpResponse("pong")),
    path("health/", health_check, name="health_check")
]


# Only add media URLs if not actively using Cloudinary
use_cloudinary = getattr(settings, 'USE_CLOUDINARY', False)
cloud_name = getattr(settings, 'CLOUDINARY_STORAGE', {}).get('CLOUD_NAME')
if not (use_cloudinary and cloud_name):
    # In development, this helper adds patterns only when DEBUG=True
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # In production (DEBUG=False), explicitly serve media from MEDIA_ROOT
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)