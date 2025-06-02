from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Item Categories
ITEM_CATEGORIES = [
    ('electronics', 'Electronics'),
    ('clothing', 'Clothing'),
    ('accessories', 'Accessories'),
    ('documents', 'Documents'),
    ('keys', 'Keys'),
    ('bags', 'Bags'),
    ('other', 'Other'),
]

# Item Status
ITEM_STATUS = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('claimed', 'Claimed'),
    ('returned', 'Returned'),
    ('rejected', 'Rejected'),
]

# Item Type
ITEM_TYPE = [
    ('lost', 'Lost'),
    ('found', 'Found'),
]

class Item(models.Model):
    """Model for lost and found items"""
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=ITEM_CATEGORIES)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    item_type = models.CharField(max_length=5, choices=ITEM_TYPE)
    status = models.CharField(max_length=10, choices=ITEM_STATUS, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    contact_info = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_item_type_display()})"

    class Meta:
        ordering = ['-created_at']

class Claim(models.Model):
    """Model for item claims"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='claims')
    claimed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claims')
    claim_date = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Claim for {self.item.name} by {self.claimed_by.username}"

    class Meta:
        ordering = ['-claim_date']

class ItemMatch(models.Model):
    """Model for potential matches between lost and found items"""
    lost_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='lost_matches')
    found_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='found_matches')
    match_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)  # Track if users were notified

    def __str__(self):
        return f"Match between {self.lost_item.name} and {self.found_item.name}"

    class Meta:
        ordering = ['-match_score']
