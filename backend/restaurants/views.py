
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
        request.user.is_superuser or
        request.user.groups.filter(name='Restaurant Owners').exists()
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
            owner=request.user,
            is_active=True
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
            owner=request.user,
            is_active=True
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
