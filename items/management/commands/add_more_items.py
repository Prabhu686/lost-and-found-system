from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from items.models import Item

class Command(BaseCommand):
    help = 'Add more diverse items for testing browse functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=25,
            help='Number of additional items to create (default: 25)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write("🎯 Adding More Items to Lost and Found Database")
        self.stdout.write("=" * 60)
        
        # Get or create test user
        try:
            user = User.objects.get(username='testuser')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )
            self.stdout.write("✅ Created test user")
        
        # Create additional users for variety
        additional_users = []
        user_data = [
            ('alice_student', 'alice@university.edu', 'Alice', 'Johnson'),
            ('bob_prof', 'bob.prof@university.edu', 'Bob', 'Smith'),
            ('carol_staff', 'carol@university.edu', 'Carol', 'Williams'),
            ('david_grad', 'david.grad@university.edu', 'David', 'Brown'),
        ]
        
        for username, email, first_name, last_name in user_data:
            try:
                additional_user = User.objects.get(username=username)
            except User.DoesNotExist:
                additional_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='testpass123',
                    first_name=first_name,
                    last_name=last_name
                )
            additional_users.append(additional_user)
        
        all_users = [user] + additional_users
        
        # Comprehensive list of items
        items_data = [
            # Electronics
            {
                'name': 'Samsung Galaxy S23',
                'category': 'electronics',
                'description': 'White Samsung Galaxy S23 with cracked screen protector. Has a purple phone case.',
                'location': 'Engineering Building - Room 205',
                'item_type': 'lost',
                'contact_info': 'tech.student@email.com'
            },
            {
                'name': 'Apple AirPods Pro',
                'category': 'electronics',
                'description': 'White AirPods Pro with charging case. Left earbud has small scratch.',
                'location': 'Music Department',
                'item_type': 'found',
                'contact_info': 'music.lover@email.com'
            },
            {
                'name': 'Dell Laptop Charger',
                'category': 'electronics',
                'description': 'Black Dell laptop charger, 65W, with frayed cable near connector.',
                'location': 'Computer Science Lab',
                'item_type': 'found',
                'contact_info': 'cs.student@email.com'
            },
            {
                'name': 'iPad Air with Keyboard',
                'category': 'electronics',
                'description': 'Silver iPad Air with blue keyboard case. Has drawing app installed.',
                'location': 'Art Studio',
                'item_type': 'lost',
                'contact_info': 'art.student@email.com'
            },
            {
                'name': 'Bluetooth Speaker',
                'category': 'electronics',
                'description': 'Small black JBL Bluetooth speaker. Still has good battery life.',
                'location': 'Outdoor Amphitheater',
                'item_type': 'found',
                'contact_info': 'event.organizer@email.com'
            },
            
            # Clothing
            {
                'name': 'Red Hoodie',
                'category': 'clothing',
                'description': 'Red university hoodie, size L, with small stain on front pocket.',
                'location': 'Dormitory Common Room',
                'item_type': 'found',
                'contact_info': 'dorm.resident@email.com'
            },
            {
                'name': 'Black Running Shoes',
                'category': 'clothing',
                'description': 'Black Nike running shoes, size 9, well-worn but good condition.',
                'location': 'Track and Field',
                'item_type': 'lost',
                'contact_info': 'runner.student@email.com'
            },
            {
                'name': 'Blue Baseball Cap',
                'category': 'clothing',
                'description': 'Blue baseball cap with university logo. Slightly faded.',
                'location': 'Baseball Field',
                'item_type': 'found',
                'contact_info': 'sports.fan@email.com'
            },
            {
                'name': 'Winter Scarf',
                'category': 'clothing',
                'description': 'Knitted winter scarf in red and white stripes. Very soft material.',
                'location': 'Main Library Entrance',
                'item_type': 'found',
                'contact_info': 'winter.student@email.com'
            },
            {
                'name': 'Leather Jacket',
                'category': 'clothing',
                'description': 'Black leather jacket, size M, with zipper pockets. Vintage style.',
                'location': 'Motorcycle Parking',
                'item_type': 'lost',
                'contact_info': 'biker.student@email.com'
            },
            
            # Accessories
            {
                'name': 'Silver Bracelet',
                'category': 'accessories',
                'description': 'Silver charm bracelet with small heart pendant. Slightly tarnished.',
                'location': 'Chemistry Lab',
                'item_type': 'found',
                'contact_info': 'chem.student@email.com'
            },
            {
                'name': 'Prescription Glasses',
                'category': 'accessories',
                'description': 'Black-rimmed prescription glasses in brown case. Strong prescription.',
                'location': 'Philosophy Department',
                'item_type': 'lost',
                'contact_info': 'philosophy.student@email.com'
            },
            {
                'name': 'Sunglasses',
                'category': 'accessories',
                'description': 'Ray-Ban style sunglasses with dark lenses. One lens has small scratch.',
                'location': 'Tennis Courts',
                'item_type': 'found',
                'contact_info': 'tennis.player@email.com'
            },
            {
                'name': 'Fitness Tracker',
                'category': 'accessories',
                'description': 'Black Fitbit fitness tracker with sport band. Needs charging.',
                'location': 'Recreation Center',
                'item_type': 'lost',
                'contact_info': 'fitness.enthusiast@email.com'
            },
            
            # Documents
            {
                'name': 'Driver\'s License',
                'category': 'documents',
                'description': 'Driver\'s license for Jennifer Martinez, expires 2026.',
                'location': 'Student Union Building',
                'item_type': 'found',
                'contact_info': 'security@university.edu'
            },
            {
                'name': 'Passport',
                'category': 'documents',
                'description': 'US Passport in blue cover. Belongs to international student.',
                'location': 'International Student Office',
                'item_type': 'found',
                'contact_info': 'international@university.edu'
            },
            {
                'name': 'Credit Cards',
                'category': 'documents',
                'description': 'Two credit cards and a debit card found together.',
                'location': 'Campus Bookstore',
                'item_type': 'found',
                'contact_info': 'bookstore@university.edu'
            },
            
            # Keys
            {
                'name': 'Dorm Room Keys',
                'category': 'keys',
                'description': 'Set of dorm keys with blue lanyard and room number tag.',
                'location': 'Residence Hall A',
                'item_type': 'found',
                'contact_info': 'housing@university.edu'
            },
            {
                'name': 'Bike Lock Key',
                'category': 'keys',
                'description': 'Small key for bike lock with red keychain.',
                'location': 'Bike Rack Area',
                'item_type': 'lost',
                'contact_info': 'cyclist@email.com'
            },
            {
                'name': 'Office Keys',
                'category': 'keys',
                'description': 'Set of office keys with faculty ID attached.',
                'location': 'Faculty Parking Lot',
                'item_type': 'found',
                'contact_info': 'faculty.services@university.edu'
            },
            
            # Bags
            {
                'name': 'Messenger Bag',
                'category': 'bags',
                'description': 'Brown leather messenger bag with laptop compartment. Contains notebooks.',
                'location': 'Business School',
                'item_type': 'found',
                'contact_info': 'business.student@email.com'
            },
            {
                'name': 'Gym Bag',
                'category': 'bags',
                'description': 'Black gym bag with workout clothes inside. Smells like detergent.',
                'location': 'Fitness Center Locker Room',
                'item_type': 'lost',
                'contact_info': 'gym.member@email.com'
            },
            {
                'name': 'Purse',
                'category': 'bags',
                'description': 'Small black purse with gold chain strap. Contains makeup items.',
                'location': 'Theater Building',
                'item_type': 'found',
                'contact_info': 'theater.student@email.com'
            },
            {
                'name': 'Camera Bag',
                'category': 'bags',
                'description': 'Professional camera bag with padding. Contains lens cleaning kit.',
                'location': 'Photography Studio',
                'item_type': 'lost',
                'contact_info': 'photographer@email.com'
            },
            
            # Other
            {
                'name': 'Water Bottle',
                'category': 'other',
                'description': 'Stainless steel water bottle with university stickers.',
                'location': 'Dining Hall',
                'item_type': 'found',
                'contact_info': 'dining.services@university.edu'
            },
            {
                'name': 'Textbook - Calculus',
                'category': 'other',
                'description': 'Calculus textbook with highlighted pages and notes in margins.',
                'location': 'Mathematics Building',
                'item_type': 'found',
                'contact_info': 'math.student@email.com'
            },
            {
                'name': 'Umbrella',
                'category': 'other',
                'description': 'Black umbrella with wooden handle. One spoke is slightly bent.',
                'location': 'Administration Building',
                'item_type': 'lost',
                'contact_info': 'staff.member@email.com'
            },
            {
                'name': 'Coffee Mug',
                'category': 'other',
                'description': 'White ceramic mug with "World\'s Best Student" text.',
                'location': 'Coffee Shop',
                'item_type': 'found',
                'contact_info': 'coffee.shop@university.edu'
            },
            {
                'name': 'Notebook',
                'category': 'other',
                'description': 'Spiral notebook with physics equations and diagrams.',
                'location': 'Physics Laboratory',
                'item_type': 'lost',
                'contact_info': 'physics.student@email.com'
            }
        ]
        
        # Create items
        created_count = 0
        skipped_count = 0
        
        # Shuffle the items and take only the requested count
        random.shuffle(items_data)
        selected_items = items_data[:count]
        
        for i, item_data in enumerate(selected_items):
            # Random user assignment
            selected_user = random.choice(all_users)
            
            # Random date within last 30 days
            days_ago = random.randint(1, 30)
            item_date = timezone.now().date() - timedelta(days=days_ago)
            
            # Random status (mostly approved for browse functionality)
            status_choices = ['approved'] * 8 + ['pending'] * 2  # 80% approved, 20% pending
            status = random.choice(status_choices)
            
            # Check if similar item exists
            existing = Item.objects.filter(
                name=item_data['name'],
                user=selected_user
            ).exists()
            
            if not existing:
                Item.objects.create(
                    user=selected_user,
                    date=item_date,
                    status=status,
                    **item_data
                )
                created_count += 1
                status_icon = "✅" if status == "approved" else "⏳"
                self.stdout.write(f"{status_icon} Created: {item_data['name']} ({item_data['item_type']}) - {status}")
            else:
                skipped_count += 1
                self.stdout.write(f"⏭️  Skipped: {item_data['name']} (already exists)")
        
        # Final statistics
        total_items = Item.objects.count()
        approved_items = Item.objects.filter(status='approved').count()
        pending_items = Item.objects.filter(status='pending').count()
        
        lost_items = Item.objects.filter(status='approved', item_type='lost').count()
        found_items = Item.objects.filter(status='approved', item_type='found').count()
        
        self.stdout.write("\n🎉 Additional Items Creation Complete!")
        self.stdout.write("=" * 50)
        self.stdout.write(f"📊 Statistics:")
        self.stdout.write(f"   Created: {created_count} new items")
        self.stdout.write(f"   Skipped: {skipped_count} existing items")
        self.stdout.write(f"   Total items: {total_items}")
        self.stdout.write(f"   Approved items: {approved_items}")
        self.stdout.write(f"   Pending items: {pending_items}")
        self.stdout.write(f"   Lost items: {lost_items}")
        self.stdout.write(f"   Found items: {found_items}")
        
        # Category breakdown
        self.stdout.write(f"\n📋 Category Breakdown:")
        categories = ['electronics', 'clothing', 'accessories', 'documents', 'keys', 'bags', 'other']
        for category in categories:
            count = Item.objects.filter(status='approved', category=category).count()
            self.stdout.write(f"   {category.title()}: {count}")
        
        self.stdout.write(f"\n🌐 Browse Items: http://127.0.0.1:8000/items/")
        self.stdout.write(f"🔍 Try different search filters and categories!")
        self.stdout.write(f"📱 Test on mobile devices for responsive design!")
