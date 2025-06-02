from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from items.models import Item
import os

class Command(BaseCommand):
    help = 'Fix image extensions from .png to .svg for proper display'

    def handle(self, *args, **options):
        self.stdout.write("🔧 Fixing Image Extensions for Proper Display")
        self.stdout.write("=" * 60)
        
        # Get items with images
        items_with_images = Item.objects.exclude(image__isnull=True).exclude(image='')
        total_items = items_with_images.count()
        
        self.stdout.write(f"📊 Found {total_items} items with images")
        
        if total_items == 0:
            self.stdout.write("❌ No items with images found!")
            return
        
        fixed_count = 0
        
        for item in items_with_images:
            try:
                # Get current image path
                current_path = item.image.path
                
                # Check if it's a PNG file with SVG content
                if current_path.endswith('.png'):
                    # Read the file content
                    with open(current_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if it's actually SVG content
                    if content.strip().startswith('<?xml') and '<svg' in content:
                        # Create new filename with .svg extension
                        new_filename = item.image.name.replace('.png', '.svg')
                        
                        # Save with correct extension
                        item.image.save(new_filename, ContentFile(content.encode('utf-8')), save=True)
                        
                        # Remove old PNG file
                        try:
                            os.remove(current_path)
                        except:
                            pass  # File might already be removed
                        
                        fixed_count += 1
                        self.stdout.write(f"✅ Fixed: {item.name} → {new_filename}")
                    else:
                        self.stdout.write(f"⏭️  Skipped: {item.name} (not SVG content)")
                else:
                    self.stdout.write(f"⏭️  Skipped: {item.name} (not PNG)")
                    
            except Exception as e:
                self.stdout.write(f"❌ Error fixing {item.name}: {e}")
        
        self.stdout.write(f"\n🎉 Successfully fixed {fixed_count} image extensions!")
        self.stdout.write("🌐 Visit browse page to see the images: http://127.0.0.1:8000/items/")
