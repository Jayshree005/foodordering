from django.conf import settings
from django.db import models
from django.db.models import Q


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
    ingredients = models.TextField(blank=True)
    allergens = models.JSONField(default=list, blank=True)
    dietary_tags = models.JSONField(default=list, blank=True)
    calories = models.PositiveIntegerField(blank=True, null=True)
    protein_g = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    is_local_specialty = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"


class RestaurantReview(models.Model):
    class Sentiment(models.TextChoices):
        POSITIVE = 'positive', 'Positive'
        NEUTRAL = 'neutral', 'Neutral'
        NEGATIVE = 'negative', 'Negative'

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='restaurant_reviews'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='review'
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    sentiment = models.CharField(max_length=10, choices=Sentiment.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=Q(rating__gte=1) & Q(rating__lte=5),
                name='restaurant_review_rating_1_to_5'
            )
        ]

    def __str__(self):
        return f'{self.restaurant.name} review by {self.customer.username}'