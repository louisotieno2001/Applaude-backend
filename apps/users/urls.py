from django.urls import path
# Import the new rate-limited views
from .views import (
    UserRegistrationView, 
    UserProfileView,
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    
    # JWT authentication endpoints using the new rate-limited views
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
