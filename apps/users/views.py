from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
)
from .serializers import UserCreateSerializer, UserDetailSerializer
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='post')
class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.
    Allows any user (anonymous) to create a new account.
    Strictly rate-limited to prevent abuse.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        logger.info(f"Registration attempt for email: {request.data.get('email')}")
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"Registration successful for email: {request.data.get('email')}")
            return response
        except Exception as e:
            logger.error(f"Registration failed for email: {request.data.get('email')}, Error: {str(e)}")
            raise

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating the authenticated user's profile.
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# --- Rate-Limited JWT Token Views ---

@method_decorator(ratelimit(key='ip', rate='20/m', method='POST', block=True), name='post')
class TokenObtainPairView(BaseTokenObtainPairView):
    """
    Custom TokenObtainPairView with IP-based rate limiting.
    """
    permission_classes = [permissions.AllowAny]

@method_decorator(ratelimit(key='ip', rate='50/m', method='POST', block=True), name='post')
class TokenRefreshView(BaseTokenRefreshView):
    """
    Custom TokenRefreshView with IP-based rate limiting.
    """
    permission_classes = [permissions.AllowAny]
