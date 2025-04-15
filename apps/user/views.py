import jwt, datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm

from rest_framework import status, generics, viewsets, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed

from .utils import get_user_from_token
from .models import (
    DispatcherProfile, WarehouseStaffProfile, DriverProfile, CustomerProfile, AccountantProfile
)
from .permissions import IsCompanyAdmin
from .serializers import (
    LoginSerializer,
    UserLogoutSerializer,
    UserPasswordResetSerializer,
    UserPasswordResetConfirmSerializer,
    UserSerializer,
    ChangePasswordSerializer,
)



# Registration View
class UserRegistrationView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user_email = serializer.validated_data['email']
            
            if get_user_model().objects.filter(email=user_email).exists():
                return Response({"message": "This email is already registered."}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            user.is_active = False
            user.save()
            
            # Generate a token for email verification
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Construct activation URL
            activation_url = f"{settings.FRONTEND_PUBLIC_URL}/account/activate/{uidb64}/{token}/"
            
            # Send activation email
            message = EmailMessage(
                subject='Activate your account',
                body=f"Hi {user.first_name} {user.last_name},\n\nPlease use the link below to activate your account.\n\nLink: {activation_url}",
                from_email=settings.EMAIL_HOST_USER, 
                to=[user.email],
            )
            message.send()
                
            return Response({
                'message': 'Registration successful. Please check your email to activate your account.',
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# AccountActivation View
class UserActivateView(APIView):
    """API view to activate a user's account"""
    permission_classes = [AllowAny]
    
    def get(self, request, uidb64, token):
        """Verify the activation token and activate the user's account"""
        try:
            # Decode the user ID from the URL-safe base64 encoding
            uid = urlsafe_base64_decode(uidb64).decode('utf-8')
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist) as e:
            return Response({'message': 'Invalid activation link or user not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if default_token_generator.check_token(user, token):
            if user.is_active:
                return Response({'message': 'Account already activated.'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.is_active = True
            user.save()
            return Response({'message': 'Your account has been activated successfully.'}, status=status.HTTP_200_OK)
        
        return Response({'message': 'Invalid activation link.'}, status=status.HTTP_400_BAD_REQUEST)
    
    


# PasswordReset View
class UserPasswordResetView(generics.GenericAPIView):
    serializer_class = UserPasswordResetSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = get_object_or_404(get_user_model(), email=email)
            
            if user:
                # Generate token and URL for password reset
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                    
                # Construct password-reset URL
                if user.role == 'client':
                    password_reset_url = f"{settings.FRONTEND_PUBLIC_URL}/client/password_reset/confirm/{uidb64}/{token}/"
                else:
                    password_reset_url = f"{settings.FRONTEND_STAFF_URL}/cooperative/password_reset/confirm/{uidb64}/{token}/"

                # Send email with password reset link
                try:
                    message = EmailMessage(
                        subject='Password Reset Requested',
                        body=f'Hi {user.first_name} {user.last_name},\n\nPlease use the link below to reset your password.\n\nLink: {password_reset_url}',
                        from_email=settings.EMAIL_HOST_USER, 
                        to=[email],
                    )
                    message.send()
                    
                    return Response({'message': 'Password reset link has been sent to your email address.'}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'message': f'Failed to send email. Please try again later.\n\nError occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'message': 'Email address not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# PasswordResetConfirm View
class UserPasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = UserPasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = get_user_model().objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                form = SetPasswordForm(user, request.data)
                if form.is_valid():
                    form.save()
                    return Response({"message": "Your password has been reset successfully."}, status=status.HTTP_200_OK)
                else:
                    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Password reset link is invalid."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Login View
class UserLoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            user = validated_data['user']
            message = validated_data['message']

            # Generate JWT token
            token = self.generate_jwt_token(user)
            login(request, user)
            response = Response(status=status.HTTP_200_OK)
            
            # Set JWT in an HttpOnly cookie
            response.set_cookie(
                key='jwt', 
                value=token,  # Use the actual token here
                httponly=False,  # JavaScript can't access this cookie
                secure=True,  # Use this in production (ensures HTTPS-only)
                samesite='Lax'  # Helps mitigate CSRF
            )

            response.data = {
                "message": message,
                "token": token
            }
            return response

        # If serializer is invalid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def generate_jwt_token(self, user):
        """Generates JWT token with user information"""
        payload = {
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),  # Token expires after 7 days
            'iat': datetime.datetime.utcnow()  # Issued at
        }

        # Encode the JWT token
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        # Return the token as a string
        return token



# Logout View\
class UserLogoutView(generics.GenericAPIView):
    serializer_class = UserLogoutSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can log out

    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK) 
        # Delete the JWT cookie
        response.delete_cookie('jwt') 
        # This will end the session
        logout(request)
        response.data = {
            'message': 'Logout success!'  # Response message
        }
        return response





class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrieve the user object using the JWT token."""
        return get_user_from_token(self.request)

    def update(self, request, *args, **kwargs):
        """Handle password change logic."""
        user = self.get_object()
        if isinstance(user, Response):  # Check if session expired and handle response
            return user

        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Set new password and update session
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)  # ✅ Ensure session is updated here too
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



