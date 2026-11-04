from django.urls import path

from .views import (
    create_restaurant,
    list_restaurants,
    restaurant_details,
    update_restaurant,
    delete_restaurant
)

urlpatterns = [
    path('', list_restaurants, name='list-restaurants'),
    path('create/', create_restaurant, name='create-restaurant'),
    path('<int:restaurant_id>/', restaurant_details, name='restaurant-details'),
    path('<int:restaurant_id>/update/', update_restaurant, name='update-restaurant'),
    path('<int:restaurant_id>/delete/', delete_restaurant, name='delete-restaurant'),
]