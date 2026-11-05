from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem


# Cart Item Serializer
class CartItemSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(
        source='food_item.name',
        read_only=True
    )

    price = serializers.DecimalField(
        source='food_item.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    image = serializers.ImageField(
        source='food_item.image',
        read_only=True
    )

    item_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'food_item',
            'food_name',
            'price',
            'image',
            'quantity',
            'customizations',
            'item_total'
        ]

    def get_item_total(self, obj):
        return obj.food_item.price * obj.quantity


# Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id',
            'restaurant',
            'items',
            'total_amount',
            'created_at'
        ]

    def get_total_amount(self, obj):
        total = 0

        for item in obj.items.all():
            total += item.food_item.price * item.quantity

        return total


# Order Item Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(
        source='food_item.name',
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'food_item',
            'food_name',
            'quantity',
            'customizations',
            'price',
            'subtotal'
        ]


# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)

    restaurant_name = serializers.CharField(
        source='restaurant.name',
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'restaurant',
            'restaurant_name',
            'customer_name',
            'delivery_address',
            'status',
            'payment_status',
            'subtotal',
            'delivery_charge',
            'total_amount',
            'estimated_preparation_time',
            'items',
            'created_at'
        ]