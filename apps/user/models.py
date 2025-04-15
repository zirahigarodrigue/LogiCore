from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

from . manager import UserManager
from apps.api.models import Company


class GENDER_CHOICES(models.TextChoices):
    SELECT = "", "Select Gender"
    MALE = "Male", "Male"
    FEMALE = "Female", "Female"


# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = [
        ("super_admin", "Super Admin"),
        ("company_admin", "Company Admin"),
        ("dispatcher", "Dispatcher"),
        ("warehouse_staff", "Warehouse Staff"),
        ("driver", "Driver"),
        ("customer", "Customer"),
        ("accountant", "Accountant"),
    ]
     
    first_name = models.CharField(verbose_name="First Name", max_length=50, blank=False)
    last_name = models.CharField(verbose_name="Last Name", max_length=50, blank=False)
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True, blank=False)
    role = models.CharField(verbose_name="Role", max_length=50, blank=False, null=False, choices=ROLE_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # access to Django admin
    date_joined = models.DateTimeField(auto_now_add=True)

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    # update django about user model
    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)





class DispatcherProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='dispatcher_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        verbose_name="Image", 
        validators=[FileExtensionValidator(['png','jpg','jpeg'])],
        upload_to='images/user/profile_images/', 
        blank=True,
        null=True
    )

    assigned_regions = models.TextField(blank=True)

    def __str__(self):
        return f"Dispatcher: {self.user.get_full_name()}"



class WarehouseStaffProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='warehouse_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        verbose_name="Image", 
        validators=[FileExtensionValidator(['png','jpg','jpeg'])],
        upload_to='images/user/profile_images/', 
        blank=True,
        null=True
    )
    warehouse_id = models.CharField(max_length=50)
    shift = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Warehouse Staff: {self.user.get_full_name()}"



class DriverProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='driver_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        verbose_name="Image", 
        validators=[FileExtensionValidator(['png','jpg','jpeg'])],
        upload_to='images/user/profile_images/', 
        blank=True,
        null=True
    )
    license_number = models.CharField(max_length=100)
    vehicle_assigned = models.CharField(max_length=100, blank=True)
    last_check_in = models.DateTimeField(null=True, blank=True)
    current_location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Driver: {self.user.get_full_name()}"



class CustomerProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='customer_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        verbose_name="Image", 
        validators=[FileExtensionValidator(['png','jpg','jpeg'])],
        upload_to='images/user/profile_images/', 
        blank=True,
        null=True
    )
    company_name = models.CharField(max_length=255)
    preferred_payment_method = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Customer: {self.user.get_full_name()}"



class AccountantProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='accountant_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        verbose_name="Image", 
        validators=[FileExtensionValidator(['png','jpg','jpeg'])],
        upload_to='images/user/profile_images/', 
        blank=True,
        null=True
    )
    employee_id = models.CharField(max_length=100)
    can_approve_invoices = models.BooleanField(default=False)

    def __str__(self):
        return f"Accountant: {self.user.get_full_name()}"

