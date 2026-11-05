
import base64
from io import BytesIO

import qrcode
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Restaurant, Category, FoodItem
from .serializers import RestaurantSerializer, CategorySerializer, FoodItemSerializer


# Create Restaurant API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_restaurant(request):

    if not (
        request.user.is_staff or
        request.user.user_type == 'restaurant_owner'
    ):
        return Response(
            {"error": "Only restaurant owners can create restaurants."},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = RestaurantSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(owner=request.user)

        return Response(
            {
                "message": "Restaurant created successfully.",
                "restaurant": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# List All Active Restaurants API
@api_view(['GET'])
def list_restaurants(request):

    restaurants = Restaurant.objects.filter(is_active=True)

    serializer = RestaurantSerializer(restaurants, many=True)

    return Response(
        {
            "total_restaurants": restaurants.count(),
            "restaurants": serializer.data
        },
        status=status.HTTP_200_OK
    )


# Restaurant Details API
@api_view(['GET'])
def restaurant_details(request, restaurant_id):

    try:
        restaurant = Restaurant.objects.get(
            id=restaurant_id,
            is_active=True
        )

    except Restaurant.DoesNotExist:
        return Response(
            {"error": "Restaurant not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = RestaurantSerializer(restaurant)

    return Response(serializer.data, status=status.HTTP_200_OK)


# Update Restaurant API
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_restaurant(request, restaurant_id):

    try:
        restaurant = Restaurant.objects.get(
            id=restaurant_id,
            **({} if request.user.is_staff else {'owner': request.user})
        )

    except Restaurant.DoesNotExist:
        return Response(
            {"error": "Restaurant not found or you are not its owner."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = RestaurantSerializer(
        restaurant,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()

        return Response(
            {
                "message": "Restaurant updated successfully.",
                "restaurant": serializer.data
            },
            status=status.HTTP_200_OK
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Delete Restaurant API (Soft Delete)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_restaurant(request, restaurant_id):

    try:
        restaurant = Restaurant.objects.get(
            id=restaurant_id,
            is_active=True,
            **({} if request.user.is_staff else {'owner': request.user})
        )

    except Restaurant.DoesNotExist:
        return Response(
            {"error": "Restaurant not found or you are not its owner."},
            status=status.HTTP_404_NOT_FOUND
        )

    restaurant.is_active = False
    restaurant.save()

    return Response(
        {"message": "Restaurant deactivated successfully."},
        status=status.HTTP_200_OK
    )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_restaurants(request):
    if request.method == 'GET':
        if request.user.is_staff:
            restaurants = Restaurant.objects.all()
        elif request.user.user_type == 'restaurant_owner':
            restaurants = Restaurant.objects.filter(owner=request.user)
        else:
            return Response({'error': 'Administrator access required.'}, status=status.HTTP_403_FORBIDDEN)
        restaurants = restaurants.order_by('id')
        return Response({
            'total_restaurants': restaurants.count(),
            'restaurants': RestaurantSerializer(restaurants, many=True).data,
        })

    if not (
        request.user.is_staff or
        request.user.user_type == 'restaurant_owner'
    ):
        return Response({'error': 'Restaurant management access required.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = RestaurantSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    restaurant = serializer.save(owner=request.user)
    return Response(
        {'message': 'Restaurant created successfully.', 'restaurant': RestaurantSerializer(restaurant).data},
        status=status.HTTP_201_CREATED
    )


def can_manage_restaurant(user, restaurant):
    return user.is_staff or restaurant.owner_id == user.id


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def restaurant_qr_code(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id, is_active=True)
    except Restaurant.DoesNotExist:
        return Response({'error': 'Restaurant not found.'}, status=status.HTTP_404_NOT_FOUND)
    if not can_manage_restaurant(request.user, restaurant):
        return Response({'error': 'You cannot manage this restaurant.'}, status=status.HTTP_403_FORBIDDEN)

    menu_url = f'{settings.FRONTEND_BASE_URL}/restaurant-menu.html?id={restaurant.id}'
    code = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )
    code.add_data(menu_url)
    code.make(fit=True)
    image = code.make_image(fill_color='black', back_color='white')
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    image_data = base64.b64encode(buffer.getvalue()).decode('ascii')
    return Response({
        'menu_url': menu_url,
        'qr_code': f'data:image/png;base64,{image_data}',
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_categories(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id, is_active=True)
    except Restaurant.DoesNotExist:
        return Response({'error': 'Restaurant not found.'}, status=status.HTTP_404_NOT_FOUND)
    if not can_manage_restaurant(request.user, restaurant):
        return Response({'error': 'You cannot manage this restaurant.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        categories = Category.objects.filter(restaurant=restaurant).order_by('name')
        return Response({
            'categories': CategorySerializer(categories, many=True).data,
        })

    data = request.data.copy()
    data['restaurant'] = restaurant.id
    serializer = CategorySerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    category = serializer.save(restaurant=restaurant)
    return Response(
        CategorySerializer(category).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_food_items(request, restaurant_id):
    try:
        restaurant = Restaurant.objects.get(pk=restaurant_id, is_active=True)
    except Restaurant.DoesNotExist:
        return Response({'error': 'Restaurant not found.'}, status=status.HTTP_404_NOT_FOUND)
    if not can_manage_restaurant(request.user, restaurant):
        return Response({'error': 'You cannot manage this restaurant.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        foods = FoodItem.objects.filter(restaurant=restaurant).select_related(
            'category'
        ).order_by('name')
        return Response({
            'food_items': FoodItemSerializer(foods, many=True).data,
        })

    data = request.data.copy()
    data['restaurant'] = restaurant.id
    serializer = FoodItemSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if serializer.validated_data['category'].restaurant_id != restaurant.id:
        return Response(
            {'category': 'Choose a category belonging to this restaurant.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    food = serializer.save(restaurant=restaurant)
    return Response(FoodItemSerializer(food).data, status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_food_item(request, food_item_id):
    try:
        food = FoodItem.objects.select_related('restaurant').get(pk=food_item_id)
    except FoodItem.DoesNotExist:
        return Response({'error': 'Food item not found.'}, status=status.HTTP_404_NOT_FOUND)
    if not can_manage_restaurant(request.user, food.restaurant):
        return Response({'error': 'You cannot manage this food item.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'DELETE':
        food.is_available = False
        food.save(update_fields=['is_available', 'updated_at'])
        return Response({'message': 'Food item marked unavailable.'}, status=status.HTTP_200_OK)

    data = request.data.copy()
    data['restaurant'] = food.restaurant_id
    serializer = FoodItemSerializer(food, data=data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    category = serializer.validated_data.get('category', food.category)
    if category.restaurant_id != food.restaurant_id:
        return Response(
            {'category': 'Choose a category belonging to this restaurant.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    updated = serializer.save()
    return Response(FoodItemSerializer(updated).data, status=status.HTTP_200_OK)


# List Categories of a Restaurant API
@api_view(['GET'])
def list_categories(request, restaurant_id):

    if not Restaurant.objects.filter(
        id=restaurant_id,
        is_active=True
    ).exists():
        return Response(
            {"error": "Restaurant not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    categories = Category.objects.filter(
        restaurant_id=restaurant_id,
        is_active=True
    )

    serializer = CategorySerializer(categories, many=True)

    return Response(
        {
            "total_categories": categories.count(),
            "categories": serializer.data
        },
        status=status.HTTP_200_OK
    )


# Category Details API
@api_view(['GET'])
def category_details(request, category_id):

    try:
        category = Category.objects.get(
            id=category_id,
            is_active=True,
            restaurant__is_active=True
        )

    except Category.DoesNotExist:
        return Response(
            {"error": "Category not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CategorySerializer(category)

    return Response(serializer.data, status=status.HTTP_200_OK)


# List Food Items of a Restaurant API
@api_view(['GET'])
def list_food_items(request, restaurant_id):

    if not Restaurant.objects.filter(
        id=restaurant_id,
        is_active=True
    ).exists():
        return Response(
            {"error": "Restaurant not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    food_items = FoodItem.objects.filter(
        restaurant_id=restaurant_id,
        restaurant__is_active=True,
        is_available=True,
        category__is_active=True
    )

    serializer = FoodItemSerializer(food_items, many=True)

    return Response(
        {
            "total_food_items": food_items.count(),
            "food_items": serializer.data
        },
        status=status.HTTP_200_OK
    )


# Food Item Details API
@api_view(['GET'])
def food_item_details(request, food_item_id):

    try:
        food_item = FoodItem.objects.get(
            id=food_item_id,
            is_available=True,
            restaurant__is_active=True,
            category__is_active=True
        )

    except FoodItem.DoesNotExist:
        return Response(
            {"error": "Food item not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = FoodItemSerializer(food_item)

    return Response(serializer.data, status=status.HTTP_200_OK)
