import re

from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password as django_validate_password
from rest_framework import serializers

from .models import User


class SignupSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'user_type',
            'preferred_language',
            'password',
            'confirm_password'
        ]

    def validate_password(self, value):

        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )

        if not re.search(r'[^A-Za-z0-9]', value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )

        try:
            django_validate_password(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages)

        return value

    def validate(self, data):

        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })

        return data

    def create(self, validated_data):

        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user