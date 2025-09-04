from django.contrib import admin
from django.urls import path, include
from apps.users.views import UserRegistrationView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Authentication endpoints for all users
    path('api/auth/register/', UserRegistrationView.as_view(), name='register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User profile endpoint
    path('api/users/', include('apps.users.urls')),

    # Include other shared app URLs if any in the future
]
