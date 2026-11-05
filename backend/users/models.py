from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.subject} - {self.email}'


class User(AbstractUser):

    class UserType(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        RESTAURANT_OWNER = 'restaurant_owner', 'Restaurant Owner'

    class Language(models.TextChoices):
        ENGLISH = 'en', 'English'
        HINDI = 'hi', 'Hindi'
        FRENCH = 'fr', 'French'
        SPANISH = 'es', 'Spanish'
        GERMAN = 'de', 'German'
        JAPANESE = 'ja', 'Japanese'

    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.CUSTOMER
    )

    phone_number = models.CharField(max_length=20, blank=True)
    delivery_address = models.TextField(blank=True)
    postal_code = models.CharField(max_length=12, blank=True)
    dietary_preferences = models.JSONField(default=list, blank=True)
    allergies = models.JSONField(default=list, blank=True)
    tourist_city = models.CharField(max_length=100, blank=True)

    preferred_language = models.CharField(
        max_length=5,
        choices=Language.choices,
        default=Language.ENGLISH
    )

    email = models.EmailField(unique=True)

    groups = models.ManyToManyField(
        Group,
        related_name='foodordering_users',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='foodordering_users',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )