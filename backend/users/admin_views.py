from django.contrib.auth import get_user_model
from django.db.models import Avg, Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import serializers

from orders.models import Order
from orders.serializers import OrderSerializer
from restaurants.models import Restaurant, RestaurantReview

User = get_user_model()


class ManagedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'user_type',
            'is_active',
            'is_staff',
        ]
        read_only_fields = ['id', 'username', 'is_staff']

    def validate_is_active(self, value):
        if self.instance == self.context['request'].user and not value:
            raise serializers.ValidationError('You cannot deactivate your own account.')
        return value


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_overview(request):
    orders = Order.objects.select_related('restaurant', 'customer').prefetch_related(
        'items__food_item'
    ).order_by('-created_at')
    status_counts = {
        key: Order.objects.filter(status=key).count()
        for key, _label in Order.OrderStatus.choices
    }

    return Response({
        'total_restaurants': Restaurant.objects.count(),
        'active_restaurants': Restaurant.objects.filter(is_active=True).count(),
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_orders': orders.count(),
        'pending_orders': status_counts.get(Order.OrderStatus.PENDING, 0),
        'preparing_orders': status_counts.get(Order.OrderStatus.PREPARING, 0),
        'delivered_orders': status_counts.get(Order.OrderStatus.DELIVERED, 0),
        'revenue': orders.exclude(
            status=Order.OrderStatus.CANCELLED
        ).aggregate(total=Sum('total_amount'))['total'] or 0,
        'total_reviews': RestaurantReview.objects.count(),
        'average_rating': RestaurantReview.objects.aggregate(
            average=Avg('rating')
        )['average'],
        'review_sentiment_counts': {
            key: RestaurantReview.objects.filter(sentiment=key).count()
            for key, _label in RestaurantReview.Sentiment.choices
        },
        'status_counts': status_counts,
        'recent_orders': OrderSerializer(orders[:10], many=True).data,
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users(request):
    users = User.objects.order_by('id')
    return Response({
        'total_users': users.count(),
        'users': ManagedUserSerializer(users, many=True).data,
    })


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def admin_user_details(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ManagedUserSerializer(
        user,
        data=request.data,
        partial=True,
        context={'request': request},
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data)
