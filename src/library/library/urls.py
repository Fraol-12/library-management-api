"""
URL configuration for library project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

# library/urls.py
from django.urls import path, include
from django.contrib import admin
from django.http import JsonResponse
from core.views import (
    BookViewSet, LoanViewSet, MeView, RegisterView,
    TestLoanPermissionView, TestPermissionView
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Router for viewsets
router = DefaultRouter()
router.register(r"books", BookViewSet, basename="books")
router.register(r"loans", LoanViewSet, basename="loan")

# Root view
def root_view(request):
    return JsonResponse({"message": "Library API is live! Visit /api/ for endpoints."})

urlpatterns = [
    path("", root_view),  # <-- this handles /
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/me/", MeView.as_view(), name="user_me"),
    path("api/test-permissions/", TestPermissionView.as_view(), name="test-permissions"),
    path("api/test-loan-permissions/", TestLoanPermissionView.as_view(), name="test-loan-permissions"),
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/", include(router.urls)),
]

