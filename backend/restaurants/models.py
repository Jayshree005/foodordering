from django.conf import settings
from django.db import models


class Restaurant(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='restaurants'
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    image = models.ImageField(
        upload_to='restaurants/',
        blank=True,
        null=True
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    is_open = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Category(models.Model):

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='categories'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"


class FoodItem(models.Model):

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='food_items'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='food_items'
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to='food_items/',
        blank=True,
        null=True
    )

    preparation_time = models.PositiveIntegerField(
        help_text="Preparation time in minutes"
    )

    is_available = models.BooleanField(default=True)
    is_vegetarian = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"