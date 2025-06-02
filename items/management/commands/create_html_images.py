from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from items.models import Item
import os

class Command(BaseCommand):
    help = 'Create HTML-based images that browsers can display'

    def handle(self, *args, **options):
        self.stdout.write("🖼️ Creating HTML-based Images")
        self.stdout.write("=" * 50)
        
        # Get items that need images
        items_to_fix = Item.objects.exclude(image__isnull=True).exclude(image='')
        total_items = items_to_fix.count()
        
        self.stdout.write(f"📊 Found {total_items} items to process")
        
        if total_items == 0:
            self.stdout.write("❌ No items found!")
            return
        
        updated_count = 0
        
        for item in items_to_fix:
            try:
                # Create an HTML file that displays as an image
                html_content = self.create_html_image(item)
                
                if html_content:
                    # Save as HTML file
                    filename = f"{item.name.lower().replace(' ', '_').replace('/', '_').replace('\"', '').replace(\"'\", '')}_{item.id}.html"
                    item.image.save(filename, ContentFile(html_content.encode('utf-8')), save=True)
                    updated_count += 1
                    self.stdout.write(f"✅ Created HTML image for: {item.name}")
                else:
                    self.stdout.write(f"⚠️  Failed to create HTML image for: {item.name}")
                    
            except Exception as e:
                self.stdout.write(f"❌ Error creating HTML image for {item.name}: {e}")
        
        self.stdout.write(f"\n🎉 Successfully created {updated_count} HTML images!")
        self.stdout.write("🌐 Visit browse page to see the images: http://127.0.0.1:8000/items/")

    def create_html_image(self, item):
        """Create an HTML file that looks like an image"""
        try:
            color = self.get_category_color(item.category)
            icon = self.get_category_icon(item.category)
            
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 0;
            width: 400px;
            height: 300px;
            background: linear-gradient(135deg, {color} 0%, {self.darken_color(color)} 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        .container {{
            z-index: 2;
            padding: 20px;
        }}
        .icon {{
            font-size: 48px;
            margin-bottom: 15px;
            background: rgba(255,255,255,0.15);
            border-radius: 50%;
            width: 80px;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-left: auto;
            margin-right: auto;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .title {{
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 8px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            line-height: 1.2;
        }}
        .category {{
            font-size: 16px;
            opacity: 0.9;
            margin-bottom: 6px;
            font-weight: 500;
        }}
        .type {{
            font-size: 14px;
            opacity: 0.8;
            margin-bottom: 12px;
            padding: 4px 12px;
            background: rgba(255,255,255,0.2);
            border-radius: 15px;
            display: inline-block;
        }}
        .location {{
            font-size: 12px;
            opacity: 0.75;
            margin-bottom: 6px;
        }}
        .date {{
            font-size: 11px;
            opacity: 0.65;
        }}
        .border {{
            position: absolute;
            top: 8px;
            left: 8px;
            right: 8px;
            bottom: 8px;
            border: 2px solid rgba(255,255,255,0.25);
            border-radius: 8px;
            z-index: 1;
        }}
        .pattern {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: radial-gradient(circle at 20% 80%, rgba(255,255,255,0.1) 0%, transparent 50%),
                              radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%);
            z-index: 1;
        }}
    </style>
</head>
<body>
    <div class="pattern"></div>
    <div class="border"></div>
    <div class="container">
        <div class="icon">{icon}</div>
        <div class="title">{self.truncate_text(item.name, 25)}</div>
        <div class="category">{item.get_category_display()}</div>
        <div class="type">{item.get_item_type_display().upper()}</div>
        <div class="location">📍 {self.truncate_text(item.location, 30)}</div>
        <div class="date">📅 {item.date.strftime('%B %d, %Y')}</div>
    </div>
</body>
</html>'''
            
            return html_content
            
        except Exception as e:
            self.stdout.write(f"Error creating HTML image for {item.name}: {e}")
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

    def darken_color(self, hex_color):
        """Darken a hex color"""
        # Simple darkening by reducing the hex values
        color_map = {
            '#3498db': '#2980b9',  # Blue
            '#9b59b6': '#8e44ad',  # Purple
            '#f1c40f': '#f39c12',  # Yellow
            '#e67e22': '#d35400',  # Orange
            '#2ecc71': '#27ae60',  # Green
            '#e74c3c': '#c0392b',  # Red
            '#95a5a6': '#7f8c8d',  # Gray
            '#34495e': '#2c3e50',  # Dark blue
        }
        return color_map.get(hex_color, '#2c3e50')

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
