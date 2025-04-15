from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User,
    DispatcherProfile,
    WarehouseStaffProfile,
    DriverProfile,
    CustomerProfile,
    AccountantProfile,
)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'company', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'role', 'company__name')
    list_filter = ('role', 'is_active', 'company')
    ordering = ('-date_joined',)

    fieldsets = (
        ("Login Credentials", {'fields': ('email', 'password')}),
        ("Personal Info", {'fields': ('first_name', 'last_name', 'role', 'company')}),
        ("Permissions", {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ("Important Dates", {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'company', 'password1', 'password2'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')


class BaseProfileAdmin(admin.ModelAdmin):
    def image_tag(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="40" style="border-radius: 4px;" />', obj.profile_image.url)
        return "-"
    image_tag.short_description = 'Profile Image'

    ordering = ('user__first_name',)
    list_filter = ('gender',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'phone')


@admin.register(DispatcherProfile)
class DispatcherProfileAdmin(BaseProfileAdmin):
    list_display = ('user', 'gender', 'phone', 'assigned_regions', 'image_tag')
    fieldsets = (
        ('User Profile', {'fields': ('user', 'gender', 'phone', 'address', 'profile_image')}),
        ('Dispatch Info', {'fields': ('assigned_regions',)}),
    )
    add_fieldsets = fieldsets


@admin.register(WarehouseStaffProfile)
class WarehouseStaffProfileAdmin(BaseProfileAdmin):
    list_display = ('user', 'gender', 'phone', 'warehouse_id', 'shift', 'is_active', 'image_tag')
    list_filter = BaseProfileAdmin.list_filter + ('is_active',)
    fieldsets = (
        ('User Profile', {'fields': ('user', 'gender', 'phone', 'address', 'profile_image')}),
        ('Warehouse Info', {'fields': ('warehouse_id', 'shift', 'is_active')}),
    )
    add_fieldsets = fieldsets


@admin.register(DriverProfile)
class DriverProfileAdmin(BaseProfileAdmin):
    list_display = ('user', 'gender', 'phone', 'license_number', 'vehicle_assigned', 'last_check_in', 'image_tag')
    fieldsets = (
        ('User Profile', {'fields': ('user', 'gender', 'phone', 'address', 'profile_image')}),
        ('Driver Info', {'fields': ('license_number', 'vehicle_assigned', 'last_check_in', 'current_location')}),
    )
    add_fieldsets = fieldsets


@admin.register(CustomerProfile)
class CustomerProfileAdmin(BaseProfileAdmin):
    list_display = ('user', 'gender', 'phone', 'company_name', 'preferred_payment_method', 'image_tag')
    fieldsets = (
        ('User Profile', {'fields': ('user', 'gender', 'phone', 'address', 'profile_image')}),
        ('Customer Info', {'fields': ('company_name', 'preferred_payment_method')}),
    )
    add_fieldsets = fieldsets


@admin.register(AccountantProfile)
class AccountantProfileAdmin(BaseProfileAdmin):
    list_display = ('user', 'gender', 'phone', 'employee_id', 'can_approve_invoices', 'image_tag')
    fieldsets = (
        ('User Profile', {'fields': ('user', 'gender', 'phone', 'address', 'profile_image')}),
        ('Accounting Info', {'fields': ('employee_id', 'can_approve_invoices')}),
    )
    add_fieldsets = fieldsets
