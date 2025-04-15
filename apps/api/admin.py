from django.contrib import admin
from django.utils.html import format_html
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'address', 'created_at')
    search_fields = ('name', 'address')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

    fieldsets = (
        ('Company Info', {
            'fields': ('name', 'logo', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = fieldsets

    readonly_fields = ('created_at',)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="60" style="border-radius: 4px;" />', obj.logo.url)
        return "-"
    logo_preview.short_description = 'Logo'
