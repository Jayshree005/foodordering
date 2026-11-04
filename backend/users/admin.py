from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('user_type', 'phone_number', 'preferred_language')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('email', 'user_type', 'phone_number', 'preferred_language')
        }),
    )

    list_display = (
        'username',
        'email',
        'user_type',
        'phone_number',
        'preferred_language',
        'is_staff'
    )