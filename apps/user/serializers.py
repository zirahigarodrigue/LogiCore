import json
from django.contrib.auth import authenticate, get_user_model, update_session_auth_hash
from django.conf import settings
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import DispatcherProfile, WarehouseStaffProfile, DriverProfile, CustomerProfile, AccountantProfile
from apps.api.models import Company



class UserPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = get_user_model().objects.get(email=value)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError('Invalid email address')

        if not user.is_active:
            raise serializers.ValidationError('User account is inactive')

        return value


class UserPasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'message':"Passwords do not match."})
        return data



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=get_user_model().ROLE_CHOICES)
    message = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        
        if not email or not password:
            raise serializers.ValidationError({'message': 'Email and password are required.'})

        # Filter user by email and role
        user = get_user_model().objects.filter(email=email, role=role).first()
        
        if user is None:
            raise serializers.ValidationError({'message': 'User not found!'})

        if not user.check_password(password):
            raise serializers.ValidationError({'message': 'Incorrect password!'})

        user = authenticate(email=email, password=password)
        
        if user and user.is_active:
            # Return user and a success message
            return {'user': user, 'message': 'Login successful!'}
        
        raise serializers.ValidationError({'message': 'User account not active!'})




class UserLogoutSerializer(serializers.Serializer):
    pass



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data["old_password"]):
            raise serializers.ValidationError({"Error": "Old password is incorrect."})

        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"Error":"New passwords do not match."})
        
        return data


    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        
         # ✅ Prevent automatic logout
        update_session_auth_hash(self.context['request'], user)
        
        return user



class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    password_confirmation = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'role', 'is_active', 'email', 'password', 'password_confirmation']
        extra_kwargs = {
            'email': {'required': False},
            'is_active': {'read_only': True, 'required': False},
            'password': {'write_only': True, 'required': False},
            'password_confirmation': {'write_only': True, 'required': False},
        }
        
        
    def validate(self, data):
        user_id = self.instance.id if self.instance else None

        # Validate email
        email = data.get('email')
        if email and self.instance and email != self.instance.email:
            existing_user = get_user_model().objects.exclude(id=user_id).filter(email=email).first()
            if existing_user:
                raise serializers.ValidationError({"email": "This email address is already in use."})

        # Validate password
        password = data.get('password')
        if password and len(password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})

        # Check password confirmation
        if 'password' in data and 'password_confirmation' in data:
            if data.get('password') != data.pop('password_confirmation', None):
                raise serializers.ValidationError("The passwords do not match.")
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirmation', None)

        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance


