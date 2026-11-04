from rest_framework import serializers
from .models import Restaurant


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