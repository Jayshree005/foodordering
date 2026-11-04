from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction
from decimal import Decimal
import uuid

from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer
from restaurants.models import FoodItem

# View Cart API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_cart(request):
    restaurant_id = request.query_params.get('restaurant_id')

    if not restaurant_id:
        return Response(
            {'error': 'Please provide restaurant_id.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        cart = Cart.objects.get(
            customer=request.user,
            restaurant_id=restaurant_id
        )
    except Cart.DoesNotExist:
        return Response(
            {'message': 'Cart is empty.', 'items': [], 'total_amount': 0},
            status=status.HTTP_200_OK
        )

    serializer = CartSerializer(cart)
    return Response(serializer.data)


# Add To Cart API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    food_item_id = request.data.get('food_item_id')
    quantity = request.data.get('quantity', 1)

    try:
        quantity = int(quantity)
        if quantity < 1:
            raise ValueError
    except (ValueError, TypeError):
        return Response(
            {'error': 'Quantity must be at least 1.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        food_item = FoodItem.objects.get(
            id=food_item_id,
            is_available=True
        )
    except (FoodItem.DoesNotExist, ValueError, TypeError):
        return Response(
            {'error': 'Food item not found or unavailable.'},
            status=status.HTTP_404_NOT_FOUND
        )

    cart, created = Cart.objects.get_or_create(
        customer=request.user,
        restaurant=food_item.restaurant
    )

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        food_item=food_item,
        defaults={'quantity': quantity}
    )

    if not item_created:
        cart_item.quantity += quantity
        cart_item.save()

    return Response(
        CartSerializer(cart).data,
        status=status.HTTP_200_OK
    )


# Update Cart Item API
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(
            id=item_id,
            cart__customer=request.user
        )
    except CartItem.DoesNotExist:
        return Response(
            {'error': 'Cart item not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    quantity = request.data.get('quantity')

    try:
        quantity = int(quantity)
        if quantity < 1:
            raise ValueError
    except (ValueError, TypeError):
        return Response(
            {'error': 'Quantity must be at least 1.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    cart_item.quantity = quantity
    cart_item.save()

    return Response(CartSerializer(cart_item.cart).data)

# Remove Cart Item API
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(
            id=item_id,
            cart__customer=request.user
        )
    except CartItem.DoesNotExist:
        return Response(
            {'error': 'Cart item not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    cart = cart_item.cart
    cart_item.delete()

    return Response(
        CartSerializer(cart).data,
        status=status.HTTP_200_OK
    )
    
# Clear Cart API
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    restaurant_id = request.data.get('restaurant_id') or request.query_params.get('restaurant_id')
    if not restaurant_id:
        return Response(
            {'error': 'Please provide restaurant_id.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        cart = Cart.objects.get(
            customer=request.user,
            restaurant_id=restaurant_id
        )
    except Cart.DoesNotExist:
        return Response(
            {'message': 'Cart is already empty.'},
            status=status.HTTP_200_OK
        )

    cart.items.all().delete()

    return Response(
        {
            'message': 'Cart cleared successfully.',
            'items': [],
            'total_amount': 0
        },
        status=status.HTTP_200_OK
    )
    
    
# Place Order API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):

    restaurant_id = request.data.get('restaurant_id')
    delivery_address = request.data.get('delivery_address')

    if not restaurant_id:
        return Response(
            {'error': 'Please provide restaurant_id.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not delivery_address or not str(delivery_address).strip():
        return Response(
            {'error': 'Please provide delivery address.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():

            cart = Cart.objects.get(
                customer=request.user,
                restaurant_id=restaurant_id
            )

            cart_items = cart.items.select_related('food_item').all()

            if not cart_items.exists():
                return Response(
                    {'error': 'Your cart is empty.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subtotal = Decimal('0.00')
            estimated_time = 0

            for item in cart_items:

                food = item.food_item

                if not food.is_available or food.restaurant_id != cart.restaurant_id:
                    return Response(
                        {'error': f'{food.name} is currently unavailable.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                item_total = food.price * item.quantity
                subtotal += item_total

                estimated_time = max(
                    estimated_time,
                    food.preparation_time
                )

            delivery_charge = Decimal('0.00')
            total_amount = subtotal + delivery_charge

            order = Order.objects.create(
                customer=request.user,
                restaurant=cart.restaurant,
                order_number=f"ORD-{uuid.uuid4().hex[:12].upper()}",
                delivery_address=str(delivery_address).strip(),
                subtotal=subtotal,
                delivery_charge=delivery_charge,
                total_amount=total_amount,
                estimated_preparation_time=estimated_time
            )

            for item in cart_items:
                food = item.food_item

                OrderItem.objects.create(
                    order=order,
                    food_item=food,
                    quantity=item.quantity,
                    price=food.price,
                    subtotal=food.price * item.quantity
                )

            cart.items.all().delete()

        return Response(
            {
                'message': 'Order placed successfully.',
                'order': OrderSerializer(order).data
            },
            status=status.HTTP_201_CREATED
        )

    except Cart.DoesNotExist:
        return Response(
            {'error': 'Cart not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
        
# My Orders API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):

    orders = Order.objects.filter(
        customer=request.user
    ).select_related(
        'restaurant'
    ).prefetch_related(
        'items__food_item'
    ).order_by('-created_at')

    serializer = OrderSerializer(orders, many=True)

    return Response(
        {
            'total_orders': orders.count(),
            'orders': serializer.data
        },
        status=status.HTTP_200_OK
    )
    
# Order Details API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_details(request, order_id):

    try:
        order = Order.objects.select_related(
            'restaurant'
        ).prefetch_related(
            'items__food_item'
        ).get(
            id=order_id,
            customer=request.user
        )

    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = OrderSerializer(order)

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )
    
# Order Tracking API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def track_order(request, order_id):

    try:
        order = Order.objects.get(
            id=order_id,
            customer=request.user
        )

    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(
        {
            'order_number': order.order_number,
            'restaurant_name': order.restaurant.name,
            'order_status': order.status,
            'payment_status': order.payment_status,
            'estimated_preparation_time': order.estimated_preparation_time,
            'created_at': order.created_at
        },
        status=status.HTTP_200_OK
    )
    
# Cancel Order API
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):

    try:
        order = Order.objects.get(
            id=order_id,
            customer=request.user
        )

    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if order.status not in [
        Order.OrderStatus.PENDING,
        Order.OrderStatus.CONFIRMED
    ]:
        return Response(
            {'error': 'This order cannot be cancelled.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    order.status = Order.OrderStatus.CANCELLED
    order.save(update_fields=['status', 'updated_at'])

    return Response(
        {
            'message': 'Order cancelled successfully.',
            'order_number': order.order_number,
            'status': order.status
        },
        status=status.HTTP_200_OK
    )
    
# Restaurant Owner - Update Order Status API
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):

    try:
        order = Order.objects.select_related(
            'restaurant',
            'restaurant__owner'
        ).get(
            id=order_id,
            restaurant__owner=request.user
        )

    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found or you do not have permission.'},
            status=status.HTTP_404_NOT_FOUND
        )

    new_status = request.data.get('status')

    allowed_statuses = [
        Order.OrderStatus.CONFIRMED,
        Order.OrderStatus.PREPARING,
        Order.OrderStatus.READY,
        Order.OrderStatus.OUT_FOR_DELIVERY,
        Order.OrderStatus.DELIVERED,
        Order.OrderStatus.CANCELLED
    ]

    if new_status not in allowed_statuses:
        return Response(
            {'error': 'Invalid order status.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    order.status = new_status
    order.save(update_fields=['status', 'updated_at'])

    return Response(
        {
            'message': 'Order status updated successfully.',
            'order_number': order.order_number,
            'status': order.status
        },
        status=status.HTTP_200_OK
    )