from collections import defaultdict
from datetime import date, timedelta
from math import ceil

from django.db.models import Avg
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from orders.models import Order, OrderItem
from restaurants.models import FoodItem
from .models import FoodProductionLog


ALLERGEN_NOTICE = (
    'Ingredient and allergen information is supplied by restaurants and may be '
    'incomplete. Always confirm directly with the restaurant; this is not a '
    'medical or allergy-safety guarantee.'
)

POSITIVE_WORDS = {
    'amazing', 'excellent', 'delicious', 'great', 'good', 'love', 'loved',
    'fresh', 'friendly', 'perfect', 'tasty', 'wonderful',
}
NEGATIVE_WORDS = {
    'bad', 'awful', 'cold', 'disappointing', 'hate', 'hated', 'late',
    'poor', 'rude', 'slow', 'stale', 'terrible', 'waste',
}


def review_sentiment(comment, rating):
    words = set(''.join(char.lower() if char.isalnum() else ' ' for char in comment).split())
    score = len(words & POSITIVE_WORDS) - len(words & NEGATIVE_WORDS)
    if rating >= 4 or score > 0:
        return 'positive'
    if rating <= 2 or score < 0:
        return 'negative'
    return 'neutral'


@api_view(['GET'])
@permission_classes([AllowAny])
def dish_recommendations(request):
    requested_diets = {
        value.strip().lower()
        for value in request.query_params.get('diet', '').split(',')
        if value.strip()
    }
    allergies = {
        value.strip().lower()
        for value in request.query_params.get('allergies', '').split(',')
        if value.strip()
    }
    if request.user.is_authenticated:
        requested_diets.update(
            str(value).strip().lower()
            for value in request.user.dietary_preferences
            if str(value).strip()
        )
        allergies.update(
            str(value).strip().lower()
            for value in request.user.allergies
            if str(value).strip()
        )

    city = request.query_params.get('city', '').strip()
    tourist_mode = request.query_params.get('mode') == 'tourist' and bool(city)
    foods = FoodItem.objects.filter(
        is_available=True,
        restaurant__is_active=True,
        restaurant__is_open=True,
        category__is_active=True,
    ).select_related('restaurant', 'category')
    if tourist_mode:
        foods = foods.filter(restaurant__city__iexact=city)

    recommendations = []
    for food in foods:
        allergens = {str(item).strip().lower() for item in food.allergens}
        ingredients = food.ingredients.lower()
        allergy_matches = allergies & allergens
        allergy_matches.update(
            allergy for allergy in allergies
            if allergy and allergy in ingredients
        )
        if allergy_matches:
            continue

        tags = {str(item).strip().lower() for item in food.dietary_tags}
        if 'vegetarian' in requested_diets and not food.is_vegetarian:
            continue
        if 'vegan' in requested_diets and 'vegan' not in tags:
            continue
        if 'gluten_free' in requested_diets and 'gluten_free' not in tags:
            continue
        if 'low_calorie' in requested_diets and (
            food.calories is None or food.calories > 450
        ):
            continue
        if 'high_protein' in requested_diets and (
            food.protein_g is None or food.protein_g < 15
        ):
            continue

        score = len(tags & requested_diets) * 10
        if 'vegetarian' in requested_diets and food.is_vegetarian:
            score += 10
        if tourist_mode and food.is_local_specialty:
            score += 15
        recommendations.append((score, food))

    recommendations.sort(
        key=lambda item: (-item[0], item[1].name.lower(), item[1].id)
    )
    serialized = [
        {
            'id': food.id,
            'name': food.name,
            'description': food.description,
            'restaurant_id': food.restaurant_id,
            'restaurant_name': food.restaurant.name,
            'city': food.restaurant.city,
            'price': str(food.price),
            'image': request.build_absolute_uri(food.image.url) if food.image else None,
            'is_vegetarian': food.is_vegetarian,
            'ingredients': food.ingredients,
            'allergens': food.allergens,
            'dietary_tags': food.dietary_tags,
            'calories': food.calories,
            'protein_g': str(food.protein_g) if food.protein_g is not None else None,
            'is_local_specialty': food.is_local_specialty,
            'match_score': score,
        }
        for score, food in recommendations[:30]
    ]
    return Response({
        'mode': 'tourist' if tourist_mode else 'diet',
        'city': city or None,
        'recommendations': serialized,
        'allergy_notice': ALLERGEN_NOTICE,
        'data_notice': (
            'Recommendations use restaurant-entered tags and nutrition values. '
            'Missing or inaccurate menu data can affect these results.'
        ),
    })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def restaurant_reviews(request, restaurant_id):
    from restaurants.models import Restaurant, RestaurantReview

    restaurant = Restaurant.objects.filter(
        pk=restaurant_id,
        is_active=True,
    ).first()
    if restaurant is None:
        return Response({'error': 'Restaurant not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Sign in to leave a review.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            order = Order.objects.get(
                pk=request.data.get('order_id'),
                customer=request.user,
                restaurant=restaurant,
                status=Order.OrderStatus.DELIVERED,
            )
        except (Order.DoesNotExist, TypeError, ValueError):
            return Response(
                {'error': 'A delivered order from this restaurant is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if hasattr(order, 'review'):
            return Response(
                {'error': 'This order already has a review.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            rating = int(request.data.get('rating'))
        except (TypeError, ValueError):
            rating = 0
        comment = str(request.data.get('comment', '')).strip()
        if rating < 1 or rating > 5 or len(comment) > 2000:
            return Response(
                {'error': 'Rating must be 1–5 and review text must be at most 2000 characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        sentiment = review_sentiment(comment, rating)
        review = RestaurantReview.objects.create(
            customer=request.user,
            restaurant=restaurant,
            order=order,
            rating=rating,
            comment=comment,
            sentiment=sentiment,
        )
        return Response({
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment,
            'sentiment': review.sentiment,
        }, status=status.HTTP_201_CREATED)

    reviews = restaurant.reviews.select_related('customer')
    return Response({
        'average_rating': reviews.aggregate(value=Avg('rating'))['value'],
        'total_reviews': reviews.count(),
        'sentiment_counts': {
            sentiment: reviews.filter(sentiment=sentiment).count()
            for sentiment, _label in RestaurantReview.Sentiment.choices
        },
        'reviews': [{
            'id': review.id,
            'customer_name': review.customer.first_name or review.customer.username,
            'rating': review.rating,
            'comment': review.comment,
            'sentiment': review.sentiment,
            'created_at': review.created_at,
        } for review in reviews[:50]],
        'sentiment_notice': (
            'Sentiment labels are a simple, rule-based summary of review wording '
            'and star ratings, not a trained language model.'
        ),
    })


def user_restaurant_scope(request, queryset):
    if request.user.is_staff:
        return queryset
    return queryset.filter(owner=request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def demand_forecast(request):
    if not (request.user.is_staff or request.user.user_type == 'restaurant_owner'):
        return Response({'error': 'Restaurant management access required.'}, status=status.HTTP_403_FORBIDDEN)

    today = timezone.localdate()
    recent_start = today - timedelta(days=14)
    previous_start = today - timedelta(days=28)
    items = OrderItem.objects.filter(
        order__restaurant__is_active=True,
        order__status__in=[
            Order.OrderStatus.PENDING,
            Order.OrderStatus.CONFIRMED,
            Order.OrderStatus.PREPARING,
            Order.OrderStatus.READY,
            Order.OrderStatus.OUT_FOR_DELIVERY,
            Order.OrderStatus.DELIVERED,
        ],
        order__created_at__date__gte=previous_start,
    ).select_related('food_item', 'order__restaurant')
    if not request.user.is_staff:
        items = items.filter(order__restaurant__owner=request.user)

    sales = defaultdict(lambda: {'recent': 0, 'previous': 0, 'recent_days': set()})
    for item in items:
        key = (item.food_item_id, item.order.restaurant_id)
        day = timezone.localtime(item.order.created_at).date()
        period = 'recent' if day >= recent_start else 'previous'
        sales[key][period] += item.quantity
        if period == 'recent':
            sales[key]['recent_days'].add(day)

    foods = FoodItem.objects.filter(
        is_available=True,
        restaurant__is_active=True,
    ).select_related('restaurant')
    if not request.user.is_staff:
        foods = foods.filter(restaurant__owner=request.user)
    forecasts = []
    for food in foods:
        sold = sales[(food.id, food.restaurant_id)]
        recent_daily = sold['recent'] / 14
        previous_daily = sold['previous'] / 14
        forecasts.append({
            'food_item_id': food.id,
            'food_name': food.name,
            'restaurant_id': food.restaurant_id,
            'restaurant_name': food.restaurant.name,
            'average_daily_sold_last_14_days': round(recent_daily, 2),
            'estimated_quantity_next_7_days': round(recent_daily * 7, 1),
            'change_percent': (
                round((recent_daily - previous_daily) / previous_daily * 100, 1)
                if previous_daily else None
            ),
            'confidence': (
                'low' if len(sold['recent_days']) < 7
                else 'medium' if len(sold['recent_days']) < 12
                else 'higher'
            ),
        })
    forecasts.sort(
        key=lambda item: (-item['estimated_quantity_next_7_days'], item['food_name'].lower())
    )
    return Response({
        'period': 'Trailing 14 days compared with the prior 14 days',
        'forecasts': forecasts,
        'method_notice': (
            'Baseline statistical estimate from recorded orders; it is not a '
            'trained AI model and does not account for holidays, stockouts, or promotions.'
        ),
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def production_logs(request):
    from restaurants.models import Restaurant

    restaurant_id = request.data.get('restaurant_id') or request.query_params.get('restaurant_id')
    logs = FoodProductionLog.objects.select_related('food_item', 'restaurant')
    if restaurant_id:
        logs = logs.filter(restaurant_id=restaurant_id)
    if not request.user.is_staff:
        if request.user.user_type != 'restaurant_owner':
            return Response({'error': 'Restaurant management access required.'}, status=status.HTTP_403_FORBIDDEN)
        logs = logs.filter(restaurant__owner=request.user)

    if request.method == 'GET':
        return Response({
            'logs': [{
                'id': log.id,
                'food_item_id': log.food_item_id,
                'food_name': log.food_item.name,
                'restaurant_id': log.restaurant_id,
                'restaurant_name': log.restaurant.name,
                'date': log.date,
                'prepared_quantity': log.prepared_quantity,
                'sold_quantity': log.sold_quantity,
                'wasted_quantity': log.wasted_quantity,
            } for log in logs[:100]],
        })

    try:
        restaurant = Restaurant.objects.get(pk=request.data.get('restaurant_id'), is_active=True)
        food = FoodItem.objects.get(
            pk=request.data.get('food_item_id'),
            restaurant=restaurant,
        )
        log_date = date.fromisoformat(str(request.data.get('date')))
        prepared = int(request.data.get('prepared_quantity'))
        sold = int(request.data.get('sold_quantity'))
        wasted = int(request.data.get('wasted_quantity', 0))
    except (Restaurant.DoesNotExist, FoodItem.DoesNotExist, TypeError, ValueError):
        return Response({'error': 'Provide a valid restaurant, food item, date, and quantities.'}, status=status.HTTP_400_BAD_REQUEST)
    if not request.user.is_staff and restaurant.owner_id != request.user.id:
        return Response({'error': 'You cannot record production for this restaurant.'}, status=status.HTTP_403_FORBIDDEN)
    if (
        prepared < 0 or sold < 0 or wasted < 0 or
        sold + wasted > prepared or log_date > timezone.localdate()
    ):
        return Response({
            'error': 'Quantities must be non-negative, sold plus wasted cannot exceed prepared quantity, and date cannot be in the future.'
        }, status=status.HTTP_400_BAD_REQUEST)

    log, _created = FoodProductionLog.objects.update_or_create(
        food_item=food,
        date=log_date,
        defaults={
            'restaurant': restaurant,
            'prepared_quantity': prepared,
            'sold_quantity': sold,
            'wasted_quantity': wasted,
            'recorded_by': request.user,
        },
    )
    return Response({'id': log.id, 'message': 'Production log saved.'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def waste_forecast(request):
    if not (request.user.is_staff or request.user.user_type == 'restaurant_owner'):
        return Response({'error': 'Restaurant management access required.'}, status=status.HTTP_403_FORBIDDEN)

    start = timezone.localdate() - timedelta(days=28)
    logs = FoodProductionLog.objects.filter(date__gte=start).select_related('food_item', 'restaurant')
    if not request.user.is_staff:
        logs = logs.filter(restaurant__owner=request.user)
    grouped = defaultdict(lambda: {'prepared': 0, 'sold': 0, 'wasted': 0, 'days': 0})
    for log in logs:
        item = grouped[(log.food_item_id, log.restaurant_id)]
        item['sold'] += log.sold_quantity
        item['wasted'] += log.wasted_quantity
        item['prepared'] += log.prepared_quantity
        item['days'] += 1

    forecasts = []
    for food_id, restaurant_id in grouped:
        totals = grouped[(food_id, restaurant_id)]
        food = FoodItem.objects.get(pk=food_id)
        waste_rate = totals['wasted'] / totals['prepared'] if totals['prepared'] else 0
        forecasts.append({
            'food_item_id': food_id,
            'food_name': food.name,
            'restaurant_id': restaurant_id,
            'restaurant_name': food.restaurant.name,
            'days_recorded': totals['days'],
            'waste_rate_percent': round(waste_rate * 100, 1),
            'average_daily_waste': round(totals['wasted'] / totals['days'], 2),
            'average_daily_sold': round(totals['sold'] / totals['days'], 2),
            'suggested_preparation_next_day': ceil(
                totals['sold'] / totals['days']
            ) if totals['days'] else 0,
            'confidence': 'low' if totals['days'] < 7 else 'medium',
        })
    forecasts.sort(key=lambda item: (-item['waste_rate_percent'], item['food_name'].lower()))
    return Response({
        'period': 'Production and waste logs from the last 28 days',
        'forecasts': forecasts,
        'method_notice': (
            'Waste estimates are historical averages, not a trained AI model. '
            'Record daily prepared and wasted quantities for meaningful results.'
        ),
    })
