from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'order_number',
        'customer',
        'restaurant',
        'total_amount',
        'status',
        'payment_status',
        'created_at',
    )

    list_filter = (
        'status',
        'payment_status',
        'restaurant',
        'created_at',
    )

    search_fields = (
        'order_number',
        'customer__username',
        'restaurant__name',
    )

    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'order',
        'food_item',
        'quantity',
        'price',
        'subtotal',
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        'customer',
        'restaurant',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'customer__username',
        'restaurant__name',
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        'cart',
        'food_item',
        'quantity',
    )