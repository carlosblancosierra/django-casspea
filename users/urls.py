from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import get_user_profile, LogoutView

urlpatterns = [
    # JWT token endpoints
    path('jwt/create/', TokenObtainPairView.as_view(), name='jwt-create'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='jwt-verify'),
    path('jwt/logout/', LogoutView.as_view(), name='jwt-logout'),
    # Djoser endpoints
    path('', include('djoser.urls')),
    # User profile endpoint
    path('profile/', get_user_profile, name='get-user-profile'),
]
