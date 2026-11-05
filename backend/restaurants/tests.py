from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import Category, FoodItem, Restaurant


class SampleRestaurantSeedTests(TestCase):
    def test_seed_command_creates_complete_demo_menus_idempotently(self):
        call_command('seed_sample_restaurants', stdout=StringIO())
        initial_restaurant_count = Restaurant.objects.count()
        initial_category_count = Category.objects.count()
        initial_food_count = FoodItem.objects.count()

        call_command('seed_sample_restaurants', stdout=StringIO())

        self.assertEqual(Restaurant.objects.count(), initial_restaurant_count)
        self.assertEqual(Category.objects.count(), initial_category_count)
        self.assertEqual(FoodItem.objects.count(), initial_food_count)
        item = FoodItem.objects.get(name='Kanda Poha')
        self.assertEqual(item.allergens, ['peanuts'])
        self.assertIn('gluten_free', item.dietary_tags)
        self.assertIsNotNone(item.calories)
        self.assertIsNotNone(item.protein_g)
        self.assertTrue(item.is_local_specialty)


class RestaurantManagementTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='restaurant-admin',
            email='restaurant-admin@example.com',
            password='test-password',
            is_staff=True
        )
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=user).key}'
        )

    def test_staff_can_create_and_list_restaurants(self):
        response = self.client.post('/api/restaurants/manage/', {
            'name': 'Managed Kitchen',
            'address': '10 Main Street',
            'city': 'Delhi',
            'phone_number': '9876543210',
            'is_open': True
        }, format='json')

        self.assertEqual(response.status_code, 201)
        listing = self.client.get('/api/restaurants/manage/')
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.data['total_restaurants'], 1)

    def test_staff_management_requires_authentication(self):
        response = APIClient().get('/api/restaurants/manage/')

        self.assertEqual(response.status_code, 401)

    def test_restaurant_owner_can_list_only_their_restaurants(self):
        owner = get_user_model().objects.create_user(
            username='restaurant-owner',
            email='restaurant-owner@example.com',
            password='test-password',
            user_type='restaurant_owner',
        )
        owned = Restaurant.objects.create(
            owner=owner,
            name='Owner Kitchen',
            address='1 Main Street',
            city='Delhi',
            phone_number='9876543210',
        )
        self.client.force_authenticate(owner)

        response = self.client.get('/api/restaurants/manage/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [restaurant['id'] for restaurant in response.data['restaurants']],
            [owned.id],
        )

    def test_restaurant_owner_can_reactivate_their_restaurant(self):
        owner = get_user_model().objects.create_user(
            username='inactive-owner',
            email='inactive-owner@example.com',
            password='test-password',
            user_type='restaurant_owner',
        )
        restaurant = Restaurant.objects.create(
            owner=owner,
            name='Closed Kitchen',
            address='2 Main Street',
            city='Delhi',
            phone_number='9876543211',
            is_active=False,
        )
        self.client.force_authenticate(owner)

        response = self.client.patch(
            f'/api/restaurants/{restaurant.id}/update/',
            {'is_active': True},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        restaurant.refresh_from_db()
        self.assertTrue(restaurant.is_active)


class MenuDataManagementTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='menu-admin',
            email='menu-admin@example.com',
            password='test-password',
            is_staff=True,
        )
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.user).key}'
        )
        self.restaurant = Restaurant.objects.create(
            owner=self.user,
            name='Menu Kitchen',
            address='2 Main Street',
            city='Delhi',
            phone_number='9876543210',
        )
        self.category = Category.objects.create(
            restaurant=self.restaurant,
            name='Mains',
        )
        self.food = FoodItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Lentil Bowl',
            price='200.00',
            preparation_time=15,
        )

    def test_staff_can_manage_menu_nutrition_and_allergen_data(self):
        response = self.client.patch(
            f'/api/restaurants/manage/food-items/{self.food.id}/',
            {
                'ingredients': 'lentils, tomato, herbs',
                'allergens': [],
                'dietary_tags': ['vegan', 'gluten_free'],
                'calories': 320,
                'protein_g': '18.50',
                'is_local_specialty': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.food.refresh_from_db()
        self.assertEqual(self.food.ingredients, 'lentils, tomato, herbs')
        self.assertEqual(self.food.dietary_tags, ['vegan', 'gluten_free'])
        self.assertEqual(self.food.protein_g, Decimal('18.50'))
        self.assertTrue(self.food.is_local_specialty)

    def test_staff_can_create_category_and_food_with_metadata(self):
        category_response = self.client.post(
            f'/api/restaurants/manage/{self.restaurant.id}/categories/',
            {'name': 'Breakfast', 'description': 'Morning meals'},
            format='json',
        )
        self.assertEqual(category_response.status_code, 201)
        category_id = category_response.data['id']

        food_response = self.client.post(
            f'/api/restaurants/manage/{self.restaurant.id}/food-items/',
            {
                'category': category_id,
                'name': 'Protein Bowl',
                'description': 'High-protein vegetarian meal',
                'price': '350.00',
                'preparation_time': 20,
                'is_vegetarian': True,
                'ingredients': 'beans, rice',
                'allergens': [],
                'dietary_tags': ['vegetarian', 'high_protein'],
                'calories': 400,
                'protein_g': '24.00',
                'is_local_specialty': False,
            },
            format='json',
        )

        self.assertEqual(food_response.status_code, 201)
        self.assertEqual(food_response.data['restaurant'], self.restaurant.id)
        self.assertEqual(food_response.data['allergens'], [])

    def test_staff_cannot_assign_category_from_another_restaurant(self):
        other_restaurant = Restaurant.objects.create(
            owner=self.user,
            name='Other Kitchen',
            address='3 Main Street',
            city='Delhi',
            phone_number='9876543211',
        )
        other_category = Category.objects.create(
            restaurant=other_restaurant,
            name='Other',
        )

        response = self.client.post(
            f'/api/restaurants/manage/{self.restaurant.id}/food-items/',
            {
                'category': other_category.id,
                'name': 'Invalid Meal',
                'price': '100.00',
                'preparation_time': 10,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)


class RestaurantQrCodeTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username='qr-owner',
            email='qr-owner@example.com',
            password='test-password',
            user_type='restaurant_owner',
        )
        self.restaurant = Restaurant.objects.create(
            owner=self.owner,
            name='QR Kitchen',
            address='4 Main Street',
            city='Delhi',
            phone_number='9876543210',
        )
        self.client = APIClient()

    def test_owner_can_generate_qr_code_for_their_menu(self):
        self.client.force_authenticate(self.owner)

        response = self.client.get(
            f'/api/restaurants/{self.restaurant.id}/qr-code/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['menu_url'],
            f'http://127.0.0.1:5500/frontend/restaurant-menu.html?id={self.restaurant.id}',
        )
        self.assertTrue(response.data['qr_code'].startswith('data:image/png;base64,'))

    def test_other_user_cannot_generate_restaurant_qr_code(self):
        other_user = get_user_model().objects.create_user(
            username='other-owner',
            email='other-owner@example.com',
            password='test-password',
            user_type='restaurant_owner',
        )
        self.client.force_authenticate(other_user)

        response = self.client.get(
            f'/api/restaurants/{self.restaurant.id}/qr-code/'
        )

        self.assertEqual(response.status_code, 403)
