from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from orders.models import Order, OrderItem
from restaurants.models import Category, FoodItem, Restaurant, RestaurantReview
from .models import FoodProductionLog


class SmartFoodFeatureTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='food-feature-owner',
            email='food-feature-owner@example.com',
            password='test-password',
            user_type='restaurant_owner',
        )
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.user).key}'
        )
        self.restaurant = Restaurant.objects.create(
            owner=self.user,
            name='Local Kitchen',
            address='1 Main Street',
            city='Delhi',
            phone_number='9876543210',
        )
        self.category = Category.objects.create(
            restaurant=self.restaurant,
            name='Mains',
        )
        self.safe_food = FoodItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Local Lentil Bowl',
            description='A local lentil specialty.',
            price=Decimal('250.00'),
            preparation_time=20,
            is_vegetarian=True,
            ingredients='lentils, tomato, herbs',
            allergens=[],
            dietary_tags=['vegetarian', 'vegan', 'gluten_free'],
            calories=320,
            protein_g=Decimal('18.00'),
            is_local_specialty=True,
        )
        self.nut_food = FoodItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Peanut Noodles',
            price=Decimal('200.00'),
            preparation_time=15,
            ingredients='noodles, peanut sauce',
            allergens=['peanuts'],
            dietary_tags=[],
        )

    def test_recommendations_filter_declared_allergens_and_diets(self):
        self.user.allergies = ['peanuts']
        self.user.dietary_preferences = ['vegan']
        self.user.save(update_fields=['allergies', 'dietary_preferences'])

        response = self.client.get('/api/recommendations/dishes/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [food['name'] for food in response.data['recommendations']],
            ['Local Lentil Bowl'],
        )
        self.assertIn('not a medical', response.data['allergy_notice'])

    def test_tourist_mode_prioritizes_local_food_in_selected_city(self):
        response = APIClient().get(
            '/api/recommendations/dishes/?mode=tourist&city=Delhi'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['mode'], 'tourist')
        self.assertEqual(
            response.data['recommendations'][0]['name'],
            'Local Lentil Bowl',
        )

    def test_customer_can_review_only_a_delivered_order(self):
        self.user.user_type = 'customer'
        self.user.save(update_fields=['user_type'])
        order = Order.objects.create(
            customer=self.user,
            restaurant=self.restaurant,
            order_number='ORD-REVIEW-TEST',
            delivery_address='1 Main Street',
            status=Order.OrderStatus.DELIVERED,
            subtotal=Decimal('250.00'),
            total_amount=Decimal('290.00'),
        )
        response = self.client.post(
            f'/api/restaurants/{self.restaurant.id}/reviews/',
            {
                'order_id': order.id,
                'rating': 5,
                'comment': 'Delicious and excellent food.',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['sentiment'], RestaurantReview.Sentiment.POSITIVE)
        duplicate = self.client.post(
            f'/api/restaurants/{self.restaurant.id}/reviews/',
            {'order_id': order.id, 'rating': 3, 'comment': ''},
            format='json',
        )
        self.assertEqual(duplicate.status_code, 400)

    def test_owner_can_record_production_for_waste_forecast(self):
        today = timezone.localdate()
        response = self.client.post(
            '/api/recommendations/admin/production-logs/',
            {
                'restaurant_id': self.restaurant.id,
                'food_item_id': self.safe_food.id,
                'date': today.isoformat(),
                'prepared_quantity': 20,
                'sold_quantity': 16,
                'wasted_quantity': 4,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(FoodProductionLog.objects.filter(food_item=self.safe_food).exists())
        forecast = self.client.get('/api/recommendations/admin/waste-forecast/')
        self.assertEqual(forecast.status_code, 200)
        item = next(
            row for row in forecast.data['forecasts']
            if row['food_item_id'] == self.safe_food.id
        )
        self.assertEqual(item['waste_rate_percent'], 20)
        self.assertIn('not a trained AI model', forecast.data['method_notice'])

    def test_demand_forecast_uses_recent_order_items(self):
        order = Order.objects.create(
            customer=self.user,
            restaurant=self.restaurant,
            order_number='ORD-FORECAST-TEST',
            delivery_address='1 Main Street',
            created_at=timezone.now() - timedelta(days=1),
            subtotal=Decimal('500.00'),
            total_amount=Decimal('540.00'),
        )
        OrderItem.objects.create(
            order=order,
            food_item=self.safe_food,
            quantity=4,
            price=self.safe_food.price,
            subtotal=Decimal('1000.00'),
        )

        response = self.client.get('/api/recommendations/admin/demand-forecast/')

        self.assertEqual(response.status_code, 200)
        item = next(
            row for row in response.data['forecasts']
            if row['food_item_id'] == self.safe_food.id
        )
        self.assertEqual(item['average_daily_sold_last_14_days'], round(4 / 14, 2))
        self.assertEqual(item['estimated_quantity_next_7_days'], 2.0)

    def test_regular_customer_cannot_access_business_forecasts(self):
        self.user.user_type = 'customer'
        self.user.save(update_fields=['user_type'])

        response = self.client.get('/api/recommendations/admin/demand-forecast/')

        self.assertEqual(response.status_code, 403)
