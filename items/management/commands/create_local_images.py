from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from items.models import Item
import os
import base64

class Command(BaseCommand):
    help = 'Create local placeholder images for items without internet connection'

    def handle(self, *args, **options):
        self.stdout.write("🖼️ Creating Local Placeholder Images")
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
        
        # Create local placeholder images
        updated_count = 0
        
        for item in items_without_images:
            try:
                image_content = self.create_simple_placeholder(item)
                
                if image_content:
                    # Save image to item
                    filename = f"{item.name.lower().replace(' ', '_').replace('/', '_')}_{item.id}.png"
                    item.image.save(filename, ContentFile(image_content), save=True)
                    updated_count += 1
                    self.stdout.write(f"✅ Added image to: {item.name}")
                else:
                    self.stdout.write(f"⚠️  Failed to create image for: {item.name}")
                    
            except Exception as e:
                self.stdout.write(f"❌ Error adding image to {item.name}: {e}")
        
        self.stdout.write(f"\n🎉 Successfully added images to {updated_count} items!")
        self.stdout.write("🌐 Visit browse page to see the images: http://127.0.0.1:8000/items/")

    def create_simple_placeholder(self, item):
        """Create a simple SVG placeholder image"""
        try:
            # Get category color
            color = self.get_category_color(item.category)
            
            # Create SVG content
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="400" height="300" fill="{color}"/>
  
  <!-- Category icon background -->
  <circle cx="200" cy="100" r="40" fill="rgba(255,255,255,0.2)"/>
  
  <!-- Category icon -->
  <text x="200" y="115" text-anchor="middle" font-family="Arial, sans-serif" font-size="30" fill="white">
    {self.get_category_icon(item.category)}
  </text>
  
  <!-- Item name -->
  <text x="200" y="160" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="white">
    {self.truncate_text(item.name, 25)}
  </text>
  
  <!-- Category -->
  <text x="200" y="185" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="rgba(255,255,255,0.9)">
    {item.get_category_display()}
  </text>
  
  <!-- Item type -->
  <text x="200" y="205" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="rgba(255,255,255,0.8)">
    {item.get_item_type_display().upper()}
  </text>
  
  <!-- Location -->
  <text x="200" y="230" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="rgba(255,255,255,0.7)">
    📍 {self.truncate_text(item.location, 30)}
  </text>
  
  <!-- Date -->
  <text x="200" y="250" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="rgba(255,255,255,0.6)">
    {item.date.strftime('%B %d, %Y')}
  </text>
  
  <!-- Border -->
  <rect x="5" y="5" width="390" height="290" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
</svg>'''
            
            # Convert SVG to PNG using a simple approach
            # Since we can't use complex libraries, we'll save as SVG and let the browser handle it
            return svg_content.encode('utf-8')
            
        except Exception as e:
            self.stdout.write(f"Error creating placeholder for {item.name}: {e}")
            return None

    def truncate_text(self, text, max_length):
        """Truncate text to max length with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    def get_category_color(self, category):
        """Get color based on category"""
        colors = {
            'electronics': '#3498db',    # Blue
            'clothing': '#9b59b6',       # Purple
            'accessories': '#f1c40f',    # Yellow
            'documents': '#e67e22',      # Orange
            'keys': '#2ecc71',           # Green
            'bags': '#e74c3c',           # Red
            'other': '#95a5a6',          # Gray
        }
        return colors.get(category, '#34495e')  # Default dark blue

    def get_category_icon(self, category):
        """Get emoji/icon based on category"""
        icons = {
            'electronics': '📱',
            'clothing': '👕',
            'accessories': '⌚',
            'documents': '📄',
            'keys': '🔑',
            'bags': '🎒',
            'other': '📦',
        }
        return icons.get(category, '❓')
