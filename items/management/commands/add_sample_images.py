from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from items.models import Item
import os
import urllib.request
import urllib.parse

class Command(BaseCommand):
    help = 'Add sample images to items using placeholder image service'

    def handle(self, *args, **options):
        self.stdout.write("🖼️ Adding Sample Images to Items")
        self.stdout.write("=" * 50)

        # Ensure media directory exists
        media_root = settings.MEDIA_ROOT
        items_dir = os.path.join(media_root, 'items')
        os.makedirs(items_dir, exist_ok=True)

        # Get items without images
        items_without_images = Item.objects.filter(image__isnull=True) | Item.objects.filter(image='')
        total_items = items_without_images.count()

        self.stdout.write(f"📊 Found {total_items} items without images")

        if total_items == 0:
            self.stdout.write("✅ All items already have images!")
            return

        # Add images to items
        updated_count = 0

        for item in items_without_images:
            try:
                image_content = self.download_placeholder_image(item)

                if image_content:
                    # Save image to item
                    filename = f"{item.name.lower().replace(' ', '_').replace('/', '_')}_{item.id}.jpg"
                    item.image.save(filename, ContentFile(image_content), save=True)
                    updated_count += 1
                    self.stdout.write(f"✅ Added image to: {item.name}")
                else:
                    self.stdout.write(f"⚠️  Failed to create image for: {item.name}")

            except Exception as e:
                self.stdout.write(f"❌ Error adding image to {item.name}: {e}")

        self.stdout.write(f"\n🎉 Successfully added images to {updated_count} items!")
        self.stdout.write("🌐 Visit browse page to see the images: http://127.0.0.1:8000/items/")

    def download_placeholder_image(self, item):
        """Download a placeholder image for the item"""
        try:
            # Create a descriptive text for the image
            text = f"{item.name} - {item.get_category_display()}"
            # URL encode the text
            encoded_text = urllib.parse.quote(text)

            # Get category color
            color = self.get_category_color_hex(item.category)

            # Create placeholder image URL (using placeholder.com service)
            url = f"https://via.placeholder.com/400x300/{color}/ffffff?text={encoded_text}"

            # Download the image
            with urllib.request.urlopen(url) as response:
                return response.read()

        except Exception as e:
            self.stdout.write(f"Error downloading image for {item.name}: {e}")
            return None

    def get_category_color_hex(self, category):
        """Get hex color based on category"""
        colors = {
            'electronics': '3498db',    # Blue
            'clothing': '9b59b6',       # Purple
            'accessories': 'f1c40f',    # Yellow
            'documents': 'e67e22',      # Orange
            'keys': '2ecc71',           # Green
            'bags': 'e74c3c',           # Red
            'other': '95a5a6',          # Gray
        }
        return colors.get(category, '34495e')  # Default dark blue
