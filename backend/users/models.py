from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


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