from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from items.models import Item
import os

class Command(BaseCommand):
    help = 'Completely fix images by removing all and creating simple CSS-based display'

    def handle(self, *args, **options):
        self.stdout.write("🔧 Completely Fixing Images")
        self.stdout.write("=" * 50)
        
        # Get all items
        all_items = Item.objects.all()
        total_items = all_items.count()
        
        self.stdout.write(f"📊 Found {total_items} items to fix")
        
        if total_items == 0:
            self.stdout.write("❌ No items found!")
            return
        
        # Clear all existing images to start fresh
        cleared_count = 0
        for item in all_items:
            if item.image:
                # Delete the file
                try:
                    if os.path.exists(item.image.path):
                        os.remove(item.image.path)
                except:
                    pass
                
                # Clear the field
                item.image = None
                item.save()
                cleared_count += 1
        
        self.stdout.write(f"🗑️ Cleared {cleared_count} existing images")
        
        # Now create simple, reliable images
        created_count = 0
        
        for item in all_items:
            try:
                # Create a simple text-based image file
                image_content = self.create_simple_image(item)
                
                if image_content:
                    # Save with simple filename
                    filename = f"item_{item.id}.txt"
                    item.image.save(filename, ContentFile(image_content.encode('utf-8')), save=True)
                    created_count += 1
                    self.stdout.write(f"✅ Created simple image for: {item.name}")
                    
            except Exception as e:
                self.stdout.write(f"❌ Error creating image for {item.name}: {e}")
        
        self.stdout.write(f"\n🎉 Successfully created {created_count} simple images!")
        self.stdout.write("🌐 Visit browse page to see the results: http://127.0.0.1:8000/items/")

    def create_simple_image(self, item):
        """Create a simple text file that we can use to trigger image display"""
        try:
            content = f"""Item: {item.name}
Category: {item.get_category_display()}
Type: {item.get_item_type_display()}
Location: {item.location}
Date: {item.date}
"""
            return content
            
        except Exception as e:
            self.stdout.write(f"Error creating simple image for {item.name}: {e}")
            return None
