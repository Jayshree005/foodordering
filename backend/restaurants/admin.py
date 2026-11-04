from django.contrib import admin
from .models import Restaurant, Category, FoodItem


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'owner',
        'city',
        'phone_number',
        'is_open',
        'is_active',
    )

    list_filter = ('city', 'is_open', 'is_active')
    search_fields = ('name', 'city', 'owner__username')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'restaurant',
        'is_active',
        'created_at',
    )

    list_filter = ('restaurant', 'is_active')
    search_fields = ('name', 'restaurant__name')


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'restaurant',
        'category',
        'price',
        'preparation_time',
        'is_available',
        'is_vegetarian',
    )

    list_filter = (
        'restaurant',
        'category',
        'is_available',
        'is_vegetarian',
    )

    search_fields = ('name', 'restaurant__name', 'category__name')