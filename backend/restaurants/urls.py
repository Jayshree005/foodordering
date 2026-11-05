from django.urls import path

from .views import (
    create_restaurant,
    list_restaurants,
    restaurant_details,
    update_restaurant,
    delete_restaurant,
    list_categories,
    category_details,
    list_food_items,
    food_item_details,
    manage_restaurants,
    manage_categories,
    manage_food_items,
    manage_food_item,
    restaurant_qr_code,
)
from recommendations.views import restaurant_reviews

urlpatterns = [
    path('manage/', manage_restaurants, name='manage-restaurants'),
    path('manage/<int:restaurant_id>/categories/', manage_categories, name='manage-categories'),
    path('manage/<int:restaurant_id>/food-items/', manage_food_items, name='manage-food-items'),
    path('manage/food-items/<int:food_item_id>/', manage_food_item, name='manage-food-item'),
    # Restaurant APIs
    path('', list_restaurants, name='list-restaurants'),
    path('create/', create_restaurant, name='create-restaurant'),
    path('<int:restaurant_id>/', restaurant_details, name='restaurant-details'),
    path('<int:restaurant_id>/update/', update_restaurant, name='update-restaurant'),
    path('<int:restaurant_id>/delete/', delete_restaurant, name='delete-restaurant'),
    path('<int:restaurant_id>/qr-code/', restaurant_qr_code, name='restaurant-qr-code'),
    path('<int:restaurant_id>/reviews/', restaurant_reviews, name='restaurant-reviews'),

    # Category APIs
    path('<int:restaurant_id>/categories/', list_categories, name='list-categories'),
    path('categories/<int:category_id>/', category_details, name='category-details'),

    # Food Item APIs
    path('<int:restaurant_id>/food-items/', list_food_items, name='list-food-items'),
    path('food-items/<int:food_item_id>/', food_item_details, name='food-item-details'),
]