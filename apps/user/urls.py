from django.urls import include, path
from rest_framework_nested.routers import SimpleRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import (
    UserRegistrationView,
    UserActivateView,
    UserPasswordResetView,
    UserPasswordResetConfirmView,
    UserLoginView, 
    UserLogoutView, 
    ChangePasswordView,
)

# Set up the main router for staff members
router = SimpleRouter()



urlpatterns = [
    path('', include(router.urls)),
    # User management
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('activate/<uidb64>/<token>/', UserActivateView.as_view(), name='user_activate'),
    path('password_reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/confirm/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('me/change_password/', ChangePasswordView.as_view(), name='change_user_password'),
    # 
]
