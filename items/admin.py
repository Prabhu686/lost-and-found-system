from django.contrib import admin
from .models import Item, Claim, ItemMatch

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'location', 'date', 'item_type', 'status', 'user')
    list_filter = ('category', 'item_type', 'status', 'date')
    search_fields = ('name', 'description', 'location')
    date_hierarchy = 'created_at'

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('item', 'claimed_by', 'claim_date', 'approved')
    list_filter = ('approved', 'claim_date')
    search_fields = ('item__name', 'claimed_by__username')

@admin.register(ItemMatch)
class ItemMatchAdmin(admin.ModelAdmin):
    list_display = ('lost_item', 'found_item', 'match_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('lost_item__name', 'found_item__name')
