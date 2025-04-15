from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, password, role='client', **extra_fields):
        """Create and save a regular user with the given first_name, last_name, email, password, and role"""
        if not email:
            raise ValueError('Email address is required.')
        if not first_name:
            raise ValueError('First name is required.')
        if not last_name:
            raise ValueError('Last name is required.')

        email = self.normalize_email(email)
        
        user = self.model(first_name=first_name, last_name=last_name, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, first_name, last_name, email, password, **extra_fields):
        """Create and save a superuser with the given first_name, last_name, email, password, and role"""
        extra_fields.setdefault('role', 'system_admin')  # Ensure role is set to system_admin for superusers
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(first_name, last_name, email, password, **extra_fields)
