#!/usr/bin/env python3
"""
home.py - Lost and Found Application Home Module
"""

import os
import sys
from datetime import datetime, timedelta

# Home page configuration
HOME_CONFIG = {
    'app_name': 'Lost and Found',
    'app_version': '1.0.0',
    'description': 'Smart Lost and Found Management System',
    'features': [
        'Smart Search & Filtering',
        'Intelligent Item Matching',
        'Mobile Responsive Design',
        'No JavaScript Dependencies',
        'User Authentication',
        'Real-time Updates'
    ],
    'contact_email': 'support@lostandfound.com',
    'max_recent_items': 6,
    'featured_categories': ['electronics', 'bags', 'keys', 'accessories']
}

def get_app_info():
    """Get application information for the home page."""
    return {
        'name': HOME_CONFIG['app_name'],
        'version': HOME_CONFIG['app_version'],
        'description': HOME_CONFIG['description'],
        'features': HOME_CONFIG['features']
    }

def get_quick_stats():
    """Get quick statistics for the home page dashboard."""
    try:
        from items.models import Item

        total_items = Item.objects.count()
        lost_items = Item.objects.filter(item_type='lost').count()
        found_items = Item.objects.filter(item_type='found').count()
        recent_items = Item.objects.filter(
            created_at__gte=datetime.now() - timedelta(days=7)
        ).count()

        return {
            'total_items': total_items,
            'lost_items': lost_items,
            'found_items': found_items,
            'recent_items': recent_items,
            'success_rate': calculate_success_rate()
        }
    except ImportError:
        return {
            'total_items': 0,
            'lost_items': 0,
            'found_items': 0,
            'recent_items': 0,
            'success_rate': 0
        }

def calculate_success_rate():
    """Calculate the success rate of item matching."""
    try:
        from items.models import Item, ItemMatch

        total_lost = Item.objects.filter(item_type='lost').count()
        if total_lost == 0:
            return 0

        matched_items = ItemMatch.objects.values('lost_item').distinct().count()
        success_rate = int((matched_items / total_lost) * 100)

        return min(success_rate, 100)
    except ImportError:
        return 85

def get_recent_items(limit=None):
    """Get recent items for the home page."""
    if limit is None:
        limit = HOME_CONFIG['max_recent_items']

    try:
        from items.models import Item

        recent_items = Item.objects.filter(
            status='approved'
        ).order_by('-created_at')[:limit]

        return [
            {
                'id': item.id,
                'name': item.name,
                'description': item.description[:100] + '...' if len(item.description) > 100 else item.description,
                'category': item.category,
                'item_type': item.item_type,
                'location': item.location,
                'date': item.date,
                'created_at': item.created_at
            }
            for item in recent_items
        ]
    except ImportError:
        return []

def get_featured_categories():
    """Get featured categories with item counts."""
    try:
        from items.models import Item

        categories = []
        for category in HOME_CONFIG['featured_categories']:
            count = Item.objects.filter(category=category, status='approved').count()
            categories.append({
                'name': category,
                'display_name': category.title(),
                'count': count,
                'icon': get_category_icon(category)
            })

        return categories
    except ImportError:
        return [
            {'name': cat, 'display_name': cat.title(), 'count': 0, 'icon': get_category_icon(cat)}
            for cat in HOME_CONFIG['featured_categories']
        ]

def get_category_icon(category):
    """Get Font Awesome icon for a category."""
    icons = {
        'electronics': 'fas fa-mobile-alt',
        'bags': 'fas fa-shopping-bag',
        'keys': 'fas fa-key',
        'accessories': 'fas fa-watch',
        'clothing': 'fas fa-tshirt',
        'documents': 'fas fa-file-alt',
        'other': 'fas fa-question-circle'
    }
    return icons.get(category, 'fas fa-question-circle')

def get_home_context():
    """Get complete context data for the home page."""
    return {
        'app_info': get_app_info(),
        'stats': get_quick_stats(),
        'recent_items': get_recent_items(),
        'featured_categories': get_featured_categories(),
        'config': HOME_CONFIG
    }

def format_item_count(count):
    """Format item count for display."""
    if count >= 1000:
        return f"{count/1000:.1f}K"
    return str(count)

def get_welcome_message():
    """Get welcome message based on time of day."""
    hour = datetime.now().hour

    if 5 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 17:
        greeting = "Good afternoon"
    elif 17 <= hour < 22:
        greeting = "Good evening"
    else:
        greeting = "Welcome"

    return f"{greeting}! Find your lost items or help others find theirs."

if __name__ == "__main__":
    print("Lost and Found - Home Module")
    print("=" * 40)

    app_info = get_app_info()
    print(f"App: {app_info['name']} v{app_info['version']}")
    print(f"Description: {app_info['description']}")

    print("\nFeatures:")
    for feature in app_info['features']:
        print(f"  ✅ {feature}")

    print(f"\nStatistics:")
    stats = get_quick_stats()
    for key, value in stats.items():
        print(f"  📊 {key.replace('_', ' ').title()}: {value}")

    print(f"\n💬 {get_welcome_message()}")
    print("\n🎉 Home module loaded successfully!")
