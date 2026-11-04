from django.urls import path

from .views import (
    view_cart,
    add_to_cart,
    update_cart_item,
    remove_cart_item,
    clear_cart,
    place_order,
    my_orders,
    order_details,
    track_order,
    cancel_order,
    update_order_status
    
)

urlpatterns = [
    path('cart/', view_cart, name='view-cart'),
    path('cart/add/', add_to_cart, name='add-to-cart'),
    path('cart/update/<int:item_id>/', update_cart_item, name='update-cart-item'),
    path('cart/remove/<int:item_id>/', remove_cart_item, name='remove-cart-item'),
    path('cart/clear/', clear_cart, name='clear-cart'),

    path('orders/place/', place_order, name='place-order'),
    path('orders/', my_orders, name='my-orders'),
    path('orders/<int:order_id>/track/', track_order, name='track-order'),
    path('orders/<int:order_id>/cancel/', cancel_order, name='cancel-order'),
    path('orders/<int:order_id>/update-status/', update_order_status, name='update-order-status'),
    path('orders/<int:order_id>/', order_details, name='order-details'),
]