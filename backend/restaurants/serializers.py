from rest_framework import serializers
from .models import Restaurant, Category, FoodItem


class RestaurantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Restaurant
        fields = [
            'id',
            'owner',
            'name',
            'description',
            'address',
            'city',
            'phone_number',
            'email',
            'image',
            'latitude',
            'longitude',
            'is_open',
            'is_active',
            'created_at',
            'updated_at'
        ]

        read_only_fields = [
            'id',
            'owner',
            'created_at',
            'updated_at'
        ]


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            'id',
            'restaurant',
            'name',
            'description',
            'image',
            'is_active',
            'created_at'
        ]

        read_only_fields = ['id', 'created_at']


class FoodItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodItem
        fields = [
            'id',
            'restaurant',
            'category',
            'name',
            'description',
            'price',
            'image',
            'preparation_time',
            'is_available',
            'is_vegetarian',
            'ingredients',
            'allergens',
            'dietary_tags',
            'calories',
            'protein_g',
            'is_local_specialty',
            'created_at',
            'updated_at'
        ]

        read_only_fields = ['id', 'created_at', 'updated_at']