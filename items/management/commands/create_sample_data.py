from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from items.models import Item

class Command(BaseCommand):
    help = 'Create sample data for testing browse items functionality'

    def handle(self, *args, **options):
        self.stdout.write("🔧 Creating Sample Data for Browse Items")
        self.stdout.write("=" * 50)
        
        # Check current status
        total_items = Item.objects.count()
        approved_items = Item.objects.filter(status='approved').count()
        
        self.stdout.write(f"📊 Current status:")
        self.stdout.write(f"   Total items: {total_items}")
        self.stdout.write(f"   Approved items: {approved_items}")
        
        # Create test user if needed
        try:
            user = User.objects.get(username='testuser')
            self.stdout.write("✅ Test user already exists")
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
            self.stdout.write("✅ Created test user")
        
        # Sample items data
        sample_items = [
            {
                'name': 'iPhone 13 Pro',
                'category': 'electronics',
                'description': 'Black iPhone 13 Pro with blue protective case. Has a small scratch on the back corner.',
                'location': 'University Library - 2nd Floor',
                'item_type': 'lost',
                'status': 'approved',
                'contact_info': 'john.doe@email.com'
            },
            {
                'name': 'Red Nike Backpack',
                'category': 'bags',
                'description': 'Red Nike backpack with laptop compartment. Contains some textbooks and a water bottle.',
                'location': 'Campus Cafeteria',
                'item_type': 'found',
                'status': 'approved',
                'contact_info': 'jane.smith@email.com'
            },
            {
                'name': 'Car Keys with Toyota Keychain',
                'category': 'keys',
                'description': 'Set of car keys with black Toyota keychain and house keys attached.',
                'location': 'Parking Lot B',
                'item_type': 'lost',
                'status': 'approved',
                'contact_info': 'mike.wilson@email.com'
            },
            {
                'name': 'Blue Denim Jacket',
                'category': 'clothing',
                'description': 'Blue denim jacket, size M, with small tear on left sleeve.',
                'location': 'Student Center',
                'item_type': 'found',
                'status': 'approved',
                'contact_info': 'sarah.jones@email.com'
            },
            {
                'name': 'Black Wallet',
                'category': 'accessories',
                'description': 'Black leather wallet with credit cards and ID inside.',
                'location': 'Gym Locker Room',
                'item_type': 'found',
                'status': 'approved',
                'contact_info': 'alex.brown@email.com'
            },
            {
                'name': 'MacBook Pro 13"',
                'category': 'electronics',
                'description': 'Silver MacBook Pro 13 inch with stickers on the back.',
                'location': 'Computer Lab',
                'item_type': 'lost',
                'status': 'approved',
                'contact_info': 'lisa.davis@email.com'
            },
            {
                'name': 'Gold Watch',
                'category': 'accessories',
                'description': 'Gold-colored wristwatch with brown leather strap.',
                'location': 'Basketball Court',
                'item_type': 'found',
                'status': 'approved',
                'contact_info': 'tom.garcia@email.com'
            },
            {
                'name': 'Student ID Card',
                'category': 'documents',
                'description': 'Student ID card for Maria Rodriguez, expires 2025.',
                'location': 'Main Entrance',
                'item_type': 'found',
                'status': 'approved',
                'contact_info': 'security@university.edu'
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for item_data in sample_items:
            # Check if similar item already exists
            existing = Item.objects.filter(
                name=item_data['name'],
                user=user
            ).exists()
            
            if not existing:
                Item.objects.create(
                    user=user,
                    date=timezone.now().date(),
                    **item_data
                )
                created_count += 1
                self.stdout.write(f"✅ Created: {item_data['name']}")
            else:
                skipped_count += 1
                self.stdout.write(f"⏭️  Skipped: {item_data['name']} (already exists)")
        
        # Final status
        final_approved = Item.objects.filter(status='approved').count()
        
        self.stdout.write("\n🎉 Sample Data Creation Complete!")
        self.stdout.write(f"   Created: {created_count} new items")
        self.stdout.write(f"   Skipped: {skipped_count} existing items")
        self.stdout.write(f"   Total approved items now: {final_approved}")
        
        if final_approved > 0:
            self.stdout.write("\n✅ Browse items should now work!")
            self.stdout.write("🌐 Visit: http://127.0.0.1:8000/items/")
        else:
            self.stdout.write("\n⚠️  Still no approved items - check admin panel")
