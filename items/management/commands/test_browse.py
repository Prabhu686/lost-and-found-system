from django.core.management.base import BaseCommand
from django.test import Client
from items.models import Item
from items.forms import ItemSearchForm

class Command(BaseCommand):
    help = 'Test browse items functionality'

    def handle(self, *args, **options):
        self.stdout.write("🧪 Testing Browse Items Functionality")
        self.stdout.write("=" * 50)
        
        # Test 1: Check database
        total_items = Item.objects.count()
        approved_items = Item.objects.filter(status='approved').count()
        
        self.stdout.write(f"📊 Database Status:")
        self.stdout.write(f"   Total items: {total_items}")
        self.stdout.write(f"   Approved items: {approved_items}")
        
        if approved_items == 0:
            self.stdout.write("❌ No approved items found!")
            self.stdout.write("💡 Run: py manage.py create_sample_data")
            return
        
        # Test 2: Check form
        try:
            form = ItemSearchForm()
            self.stdout.write("✅ ItemSearchForm works")
        except Exception as e:
            self.stdout.write(f"❌ ItemSearchForm error: {e}")
            return
        
        # Test 3: Check browse page
        try:
            client = Client()
            response = client.get('/items/')
            
            if response.status_code == 200:
                self.stdout.write("✅ Browse page loads successfully")
                
                # Check if items are in context
                if 'page_obj' in response.context:
                    items_count = len(response.context['page_obj'])
                    self.stdout.write(f"✅ Found {items_count} items on page")
                    
                    if items_count > 0:
                        # Show first few items
                        self.stdout.write("📋 Sample items:")
                        for item in response.context['page_obj'][:3]:
                            self.stdout.write(f"   - {item.name} ({item.item_type})")
                    else:
                        self.stdout.write("⚠️  No items in page context")
                else:
                    self.stdout.write("❌ page_obj missing from context")
                    return
            else:
                self.stdout.write(f"❌ Browse page failed: HTTP {response.status_code}")
                return
                
        except Exception as e:
            self.stdout.write(f"❌ Browse page error: {e}")
            return
        
        # Test 4: Test search functionality
        try:
            # Test search with filters
            response = client.get('/items/?search=iPhone')
            if response.status_code == 200:
                self.stdout.write("✅ Search functionality works")
            else:
                self.stdout.write("❌ Search functionality failed")
                
            # Test category filter
            response = client.get('/items/?category=electronics')
            if response.status_code == 200:
                self.stdout.write("✅ Category filter works")
            else:
                self.stdout.write("❌ Category filter failed")
                
        except Exception as e:
            self.stdout.write(f"❌ Search test error: {e}")
        
        # Test 5: Show item breakdown
        self.stdout.write("\n📊 Item Breakdown:")
        lost_items = Item.objects.filter(status='approved', item_type='lost').count()
        found_items = Item.objects.filter(status='approved', item_type='found').count()
        
        self.stdout.write(f"   Lost items: {lost_items}")
        self.stdout.write(f"   Found items: {found_items}")
        
        # Show categories
        categories = Item.objects.filter(status='approved').values_list('category', flat=True).distinct()
        self.stdout.write(f"   Categories: {', '.join(categories)}")
        
        self.stdout.write("\n🎉 Browse Items Functionality Test Complete!")
        self.stdout.write("🌐 Visit: http://127.0.0.1:8000/items/")
        self.stdout.write("🔍 Try searching and filtering items")
