from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from restaurants.models import Category, FoodItem, Restaurant
from orders.models import Order


class CartEndpointTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='cart-customer',
            email='cart-customer@example.com',
            password='test-password'
        )
        self.client = APIClient()
        self.user = user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=user).key}'
        )
        restaurant = Restaurant.objects.create(
            owner=user,
            name='Test Kitchen',
            address='1 Test Street',
            city='Delhi',
            phone_number='9876543210'
        )
        category = Category.objects.create(restaurant=restaurant, name='Mains')
        self.food = FoodItem.objects.create(
            restaurant=restaurant,
            category=category,
            name='Test Meal',
            price=Decimal('250.00'),
            preparation_time=20
        )
        self.restaurant = restaurant

    def test_lists_empty_authenticated_carts(self):
        response = self.client.get('/api/cart/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'carts': []})

    def test_cart_and_order_use_backend_records(self):
        add_response = self.client.post('/api/cart/add/', {
            'food_item_id': self.food.id,
            'quantity': 2,
            'customizations': ['no onion', 'less spicy']
        }, format='json')
        self.assertEqual(add_response.status_code, 200)

        cart_response = self.client.get('/api/cart/')
        self.assertEqual(cart_response.status_code, 200)
        self.assertEqual(cart_response.data['carts'][0]['items'][0]['quantity'], 2)

        order_response = self.client.post('/api/orders/place/', {
            'restaurant_id': self.restaurant.id,
            'delivery_address': '12 Main Street, Delhi'
        }, format='json')
        self.assertEqual(order_response.status_code, 201)
        self.assertEqual(order_response.data['order']['total_amount'], '540.00')
        self.assertEqual(
            order_response.data['order']['items'][0]['customizations'],
            ['no onion', 'less spicy']
        )
        self.assertEqual(self.client.get('/api/cart/').data, {'carts': []})

    def test_admin_order_list_requires_staff(self):
        response = self.client.get('/api/orders/admin/')

        self.assertEqual(response.status_code, 403)

    def test_same_food_can_be_added_with_different_customizations(self):
        first = self.client.post('/api/cart/add/', {
            'food_item_id': self.food.id,
            'quantity': 1,
            'customizations': ['no onion']
        }, format='json')
        second = self.client.post('/api/cart/add/', {
            'food_item_id': self.food.id,
            'quantity': 1,
            'customizations': ['extra cheese']
        }, format='json')

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(
            len(self.client.get('/api/cart/').data['carts'][0]['items']),
            2
        )

    def test_cart_rejects_unsupported_customization(self):
        response = self.client.post('/api/cart/add/', {
            'food_item_id': self.food.id,
            'quantity': 1,
            'customizations': ['free item']
        }, format='json')

        self.assertEqual(response.status_code, 400)

    def test_staff_can_update_order_status(self):
        order = Order.objects.create(
            customer=self.user,
            restaurant=self.restaurant,
            order_number='ORD-TEST-STATUS',
            delivery_address='1 Test Street',
            subtotal=Decimal('250.00'),
            delivery_charge=Decimal('40.00'),
            total_amount=Decimal('290.00')
        )
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])

        response = self.client.patch(
            f'/api/orders/{order.id}/update-status/',
            {'status': Order.OrderStatus.READY},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.READY)
