from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class ProfileEndpointTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='profile-customer',
            email='profile-customer@example.com',
            password='test-password'
        )
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.user).key}'
        )

    def test_profile_can_be_read_and_updated(self):
        response = self.client.patch('/api/users/profile/', {
            'first_name': 'Alex',
            'phone_number': '9876543210',
            'delivery_address': '12 Main Street',
            'postal_code': '110001'
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Alex')
        self.assertEqual(self.user.phone_number, '9876543210')
        self.assertEqual(self.user.delivery_address, '12 Main Street')
        self.assertEqual(self.user.postal_code, '110001')

    def test_profile_requires_authentication(self):
        response = APIClient().get('/api/users/profile/')

        self.assertEqual(response.status_code, 401)

    def test_profile_reports_staff_access_without_allowing_changes(self):
        response = self.client.patch(
            '/api/users/profile/',
            {'is_staff': True},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['is_staff'])
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)

    def test_profile_reports_staff_users(self):
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])

        response = self.client.get('/api/users/profile/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_staff'])

    def test_profile_preferences_are_persisted(self):
        response = self.client.patch('/api/users/profile/', {
            'dietary_preferences': ['vegetarian', 'low_calorie'],
            'allergies': ['peanuts'],
            'tourist_city': 'Delhi'
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.dietary_preferences, ['vegetarian', 'low_calorie'])
        self.assertEqual(self.user.allergies, ['peanuts'])
        self.assertEqual(self.user.tourist_city, 'Delhi')

    def test_login_returns_authentication_token(self):
        response = APIClient().post('/api/users/login/', {
            'email': self.user.email,
            'password': 'test-password'
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['token'])

    def test_signup_creates_user_and_token(self):
        response = APIClient().post('/api/users/signup/', {
            'username': 'new-customer',
            'first_name': 'New',
            'last_name': 'Customer',
            'email': 'new-customer@example.com',
            'password': 'StrongPass#2026',
            'confirm_password': 'StrongPass#2026'
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['token'])
        self.assertTrue(
            Token.objects.filter(user__email='new-customer@example.com').exists()
        )

    def test_admin_overview_requires_staff(self):
        response = self.client.get('/api/users/admin/overview/')

        self.assertEqual(response.status_code, 403)

    def test_admin_overview_returns_real_counts(self):
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])

        response = self.client.get('/api/users/admin/overview/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('total_users', response.data)
        self.assertIn('recent_orders', response.data)

    def test_staff_can_update_user_email(self):
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])

        response = self.client.patch(
            f'/api/users/admin/users/{self.user.id}/',
            {'email': 'updated@example.com'},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')

    def test_contact_message_is_saved(self):
        response = APIClient().post('/api/users/contact/', {
            'name': 'Customer',
            'email': 'customer@example.com',
            'subject': 'Order Issue',
            'message': 'Please help with my order.'
        }, format='json')

        self.assertEqual(response.status_code, 201)
        from users.models import ContactMessage
        self.assertTrue(ContactMessage.objects.filter(email='customer@example.com').exists())
