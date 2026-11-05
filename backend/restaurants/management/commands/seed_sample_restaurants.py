from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from restaurants.models import Category, FoodItem, Restaurant


SAMPLE_RESTAURANTS = [
    {
        'name': 'Jaipur Heritage Kitchen',
        'description': 'Sample restaurant showcasing Rajasthani home-style dishes. Sample menu and nutrition figures are for demonstration and should be verified before service.',
        'address': '12 MI Road',
        'city': 'Jaipur',
        'phone_number': '9000001001',
        'email': 'jaipur@example.invalid',
        'categories': {
            'Rajasthani Starters': [
                {
                    'name': 'Pyaaz Kachori',
                    'description': 'Crisp pastry filled with spiced onion.',
                    'price': '90.00',
                    'preparation_time': 15,
                    'is_vegetarian': True,
                    'ingredients': 'wheat flour, onion, lentils, spices, oil',
                    'allergens': ['gluten'],
                    'dietary_tags': ['vegetarian'],
                    'calories': 290,
                    'protein_g': '7.00',
                    'is_local_specialty': True,
                },
                {
                    'name': 'Mirchi Vada',
                    'description': 'Mild green chilli stuffed with seasoned potato and fried in gram-flour batter.',
                    'price': '110.00',
                    'preparation_time': 18,
                    'is_vegetarian': True,
                    'ingredients': 'green chilli, potato, gram flour, spices, oil',
                    'allergens': [],
                    'dietary_tags': ['vegetarian', 'gluten_free'],
                    'calories': 240,
                    'protein_g': '6.00',
                    'is_local_specialty': True,
                },
            ],
            'Rajasthani Mains': [
                {
                    'name': 'Dal Baati Churma',
                    'description': 'Baked wheat baati served with lentils and sweet churma.',
                    'price': '280.00',
                    'preparation_time': 35,
                    'is_vegetarian': True,
                    'ingredients': 'wheat, lentils, ghee, jaggery, spices',
                    'allergens': ['gluten', 'milk'],
                    'dietary_tags': ['vegetarian'],
                    'calories': 720,
                    'protein_g': '22.00',
                    'is_local_specialty': True,
                },
                {
                    'name': 'Gatte Ki Sabzi with Rice',
                    'description': 'Gram-flour dumplings in spiced yoghurt gravy with steamed rice.',
                    'price': '240.00',
                    'preparation_time': 30,
                    'is_vegetarian': True,
                    'ingredients': 'gram flour, yoghurt, rice, tomato, spices',
                    'allergens': ['milk'],
                    'dietary_tags': ['vegetarian', 'gluten_free'],
                    'calories': 560,
                    'protein_g': '19.00',
                    'is_local_specialty': True,
                },
            ],
            'Sweets and Drinks': [
                {
                    'name': 'Ghewar',
                    'description': 'Traditional honeycomb-style sweet finished with milk solids.',
                    'price': '130.00',
                    'preparation_time': 20,
                    'is_vegetarian': True,
                    'ingredients': 'wheat flour, milk, sugar, ghee',
                    'allergens': ['gluten', 'milk'],
                    'dietary_tags': ['vegetarian'],
                    'calories': 410,
                    'protein_g': '8.00',
                    'is_local_specialty': True,
                },
            ],
        },
    },
    {
        'name': 'Mumbai Coastal Table',
        'description': 'Sample coastal-style kitchen featuring Maharashtrian and Konkan-inspired dishes. Sample menu and nutrition figures are estimates for demonstration.',
        'address': '8 Linking Road',
        'city': 'Mumbai',
        'phone_number': '9000001002',
        'email': 'mumbai@example.invalid',
        'categories': {
            'Street Snacks': [
                {
                    'name': 'Vada Pav',
                    'description': 'Spiced potato fritter in a soft bun with chutneys.',
                    'price': '75.00',
                    'preparation_time': 12,
                    'is_vegetarian': True,
                    'ingredients': 'potato, wheat bun, gram flour, garlic, chutneys',
                    'allergens': ['gluten'],
                    'dietary_tags': ['vegetarian'],
                    'calories': 330,
                    'protein_g': '8.00',
                    'is_local_specialty': True,
                },
                {
                    'name': 'Kanda Poha',
                    'description': 'Flattened rice cooked with onion, peanuts, turmeric and lemon.',
                    'price': '100.00',
                    'preparation_time': 15,
                    'is_vegetarian': True,
                    'ingredients': 'flattened rice, onion, peanuts, curry leaves, lemon',
                    'allergens': ['peanuts'],
                    'dietary_tags': ['vegetarian', 'gluten_free'],
                    'calories': 280,
                    'protein_g': '7.00',
                    'is_local_specialty': True,
                },
            ],
            'Coastal Mains': [
                {
                    'name': 'Malvani Fish Curry with Rice',
                    'description': 'Fish in a coconut and spice curry served with steamed rice.',
                    'price': '360.00',
                    'preparation_time': 32,
                    'is_vegetarian': False,
                    'ingredients': 'fish, coconut, rice, tamarind, spices',
                    'allergens': ['fish'],
                    'dietary_tags': ['gluten_free', 'high_protein'],
                    'calories': 590,
                    'protein_g': '34.00',
                    'is_local_specialty': True,
                },
                {
                    'name': 'Pav Bhaji',
                    'description': 'Buttered bread rolls served with mashed spiced vegetables.',
                    'price': '220.00',
                    'preparation_time': 25,
                    'is_vegetarian': True,
                    'ingredients': 'potato, cauliflower, peas, tomato, wheat bread, butter',
                    'allergens': ['gluten', 'milk'],
                    'dietary_tags': ['vegetarian'],
                    'calories': 610,
                    'protein_g': '15.00',
                    'is_local_specialty': True,
                },
            ],
            'Desserts and Drinks': [
                {
                    'name': 'Sol Kadhi',
                    'description': 'Chilled kokum and coconut drink with a gentle spice finish.',
                    'price': '90.00',
                    'preparation_time': 5,
                    'is_vegetarian': True,
                    'ingredients': 'coconut milk, kokum, garlic, coriander',
                    'allergens': [],
                    'dietary_tags': ['vegetarian', 'vegan', 'gluten_free'],
                    'calories': 110,
                    'protein_g': '2.00',
                    'is_local_specialty': True,
                },
            ],
        },
    },
    {
        'name': 'Bengaluru Garden Cafe',
        'description': 'Sample South Indian cafe with breakfast, plant-based options and Karnataka specialties. Sample menu and nutrition figures are estimates for demonstration.',
        'address': '21 Indiranagar Main Road',
        'city': 'Bengaluru',
        'phone_number': '9000001003',
        'email': 'bengaluru@example.invalid',
        'categories': {
            'Breakfast': [
                {
                    'name': 'Masala Dosa',
                    'description': 'Crisp fermented rice and lentil crepe filled with spiced potato.',
                    'price': '150.00',
                    'preparation_time': 20,
                    'is_vegetarian': True,
                    'ingredients': 'rice, lentils, potato, onion, spices',
                    'allergens': [],
                    'dietary_tags': ['vegetarian', 'vegan', 'gluten_free'],
                    'calories': 390,
                    'protein_g': '11.00',
                    'is_local_specialty': True,
                },
                {
                    'name': 'Ragi Idli',
                    'description': 'Steamed finger-millet and lentil cakes with coconut chutney.',
                    'price': '120.00',
                    'preparation_time': 18,
                    'is_vegetarian': True,
                    'ingredients': 'ragi, rice, lentils, coconut, mustard seeds',
                    'allergens': [],
                    'dietary_tags': ['vegetarian', 'vegan', 'gluten_free'],
                    'calories': 250,
                    'protein_g': '10.00',
                    'is_local_specialty': True,
                },
            ],
            'Cafe Mains': [
                {
                    'name': 'Bisi Bele Bath',
                    'description': 'Rice, lentils and vegetables simmered with Karnataka spice blend.',
                    'price': '190.00',
                    'preparation_time': 28,
                    'is_vegetarian': True,
                    'ingredients': 'rice, lentils, vegetables, tamarind, spices',
                    'allergens': [],
                    'dietary_tags': ['vegetarian', 'vegan', 'gluten_free'],
                    'calories': 460,
                    'protein_g': '16.00',
                    'is_local_specialty': True,
                },
                {
                    'name': 'Paneer Pepper Bowl',
                    'description': 'Pepper-seasoned paneer with vegetables and steamed rice.',
                    'price': '260.00',
                    'preparation_time': 24,
                    'is_vegetarian': True,
                    'ingredients': 'paneer, rice, bell pepper, onion, spices',
                    'allergens': ['milk'],
                    'dietary_tags': ['vegetarian', 'gluten_free', 'high_protein'],
                    'calories': 520,
                    'protein_g': '27.00',
                    'is_local_specialty': False,
                },
            ],
            'Bakery and Drinks': [
                {
                    'name': 'Filter Coffee',
                    'description': 'South Indian style coffee prepared with milk.',
                    'price': '70.00',
                    'preparation_time': 7,
                    'is_vegetarian': True,
                    'ingredients': 'coffee, milk, sugar',
                    'allergens': ['milk'],
                    'dietary_tags': ['vegetarian', 'gluten_free'],
                    'calories': 120,
                    'protein_g': '4.00',
                    'is_local_specialty': True,
                },
            ],
        },
    },
]


class Command(BaseCommand):
    help = 'Add clearly labelled sample restaurants and menus for local development.'

    def handle(self, *args, **options):
        user_model = get_user_model()
        owner = user_model.objects.filter(is_active=True, is_staff=True).order_by('id').first()
        if owner is None:
            owner, created = user_model.objects.get_or_create(
                username='smartdine-sample-owner',
                defaults={
                    'email': 'sample-owner@example.invalid',
                    'user_type': user_model.UserType.RESTAURANT_OWNER,
                    'is_active': False,
                },
            )
            if created:
                owner.set_unusable_password()
                owner.save(update_fields=['password'])

        created_restaurants = 0
        created_categories = 0
        created_food_items = 0

        for sample in SAMPLE_RESTAURANTS:
            restaurant_data = {
                key: value for key, value in sample.items() if key != 'categories'
            }
            restaurant, created = Restaurant.objects.get_or_create(
                owner=owner,
                name=sample['name'],
                defaults=restaurant_data,
            )
            created_restaurants += int(created)

            for category_name, menu in sample['categories'].items():
                category, created = Category.objects.get_or_create(
                    restaurant=restaurant,
                    name=category_name,
                    defaults={
                        'description': f'Sample {category_name.lower()} menu for demonstration.',
                    },
                )
                created_categories += int(created)

                for item in menu:
                    _, created = FoodItem.objects.get_or_create(
                        restaurant=restaurant,
                        category=category,
                        name=item['name'],
                        defaults=item,
                    )
                    created_food_items += int(created)

        self.stdout.write(self.style.SUCCESS(
            'Sample data ready: '
            f'{created_restaurants} restaurant(s), '
            f'{created_categories} categor(ies), '
            f'{created_food_items} menu item(s) created.'
        ))
        self.stdout.write(
            'Menu descriptions identify nutrition values as estimates; '
            'verify ingredients and allergen declarations before serving.'
        )
