from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from items.models import Item, Claim, ItemMatch
from django.contrib.auth.models import User
from datetime import timedelta
import difflib

class Command(BaseCommand):
    help = 'Enhance success rate with automated matching and notifications'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Enhancing Success Rate")
        self.stdout.write("=" * 50)
        
        # Run all enhancement features
        self.create_automatic_matches()
        self.send_match_notifications()
        self.send_reminder_notifications()
        self.update_success_metrics()
        
        self.stdout.write("\n🎉 Success rate enhancement completed!")

    def create_automatic_matches(self):
        """Create automatic matches between lost and found items"""
        self.stdout.write("\n🔍 Creating Automatic Matches...")
        
        lost_items = Item.objects.filter(item_type='lost', status='approved')
        found_items = Item.objects.filter(item_type='found', status='approved')
        
        matches_created = 0
        
        for lost_item in lost_items:
            for found_item in found_items:
                # Skip if match already exists
                if ItemMatch.objects.filter(lost_item=lost_item, found_item=found_item).exists():
                    continue
                
                # Calculate match score
                score = self.calculate_match_score(lost_item, found_item)
                
                if score >= 70:  # 70% match threshold
                    match = ItemMatch.objects.create(
                        lost_item=lost_item,
                        found_item=found_item,
                        match_score=score,
                        created_at=timezone.now()
                    )
                    matches_created += 1
                    self.stdout.write(f"✅ Match created: {lost_item.name} ↔ {found_item.name} (Score: {score}%)")
        
        self.stdout.write(f"📊 Created {matches_created} new automatic matches")

    def calculate_match_score(self, lost_item, found_item):
        """Calculate similarity score between lost and found items"""
        score = 0
        
        # Category match (30 points)
        if lost_item.category == found_item.category:
            score += 30
        
        # Name similarity (25 points)
        name_similarity = difflib.SequenceMatcher(None, 
            lost_item.name.lower(), found_item.name.lower()).ratio()
        score += int(name_similarity * 25)
        
        # Description similarity (20 points)
        desc_similarity = difflib.SequenceMatcher(None, 
            lost_item.description.lower(), found_item.description.lower()).ratio()
        score += int(desc_similarity * 20)
        
        # Location proximity (15 points)
        location_similarity = difflib.SequenceMatcher(None, 
            lost_item.location.lower(), found_item.location.lower()).ratio()
        score += int(location_similarity * 15)
        
        # Date proximity (10 points)
        date_diff = abs((lost_item.date - found_item.date).days)
        if date_diff <= 1:
            score += 10
        elif date_diff <= 3:
            score += 7
        elif date_diff <= 7:
            score += 5
        elif date_diff <= 14:
            score += 3
        
        return min(score, 100)  # Cap at 100%

    def send_match_notifications(self):
        """Send notifications for new matches"""
        self.stdout.write("\n📧 Sending Match Notifications...")

        # Get all matches and filter in Python (MongoDB compatibility)
        all_matches = ItemMatch.objects.all()
        recent_matches = []

        cutoff_time = timezone.now() - timedelta(hours=24)

        for match in all_matches:
            if match.created_at >= cutoff_time and not match.notified:
                recent_matches.append(match)

        notifications_sent = 0

        for match in recent_matches:
            # Notify lost item owner
            self.send_match_email(
                match.lost_item.user,
                match.lost_item,
                match.found_item,
                'lost',
                match.match_score
            )

            # Notify found item owner
            self.send_match_email(
                match.found_item.user,
                match.found_item,
                match.lost_item,
                'found',
                match.match_score
            )

            # Mark as notified
            match.notified = True
            match.save()

            notifications_sent += 2

        self.stdout.write(f"📧 Sent {notifications_sent} match notifications")

    def send_match_email(self, user, user_item, matched_item, item_type, score):
        """Send email notification about a potential match"""
        subject = f"🎯 Potential Match Found for Your {item_type.title()} Item!"
        
        message = f"""
Hi {user.username},

Great news! We found a potential match for your {item_type} item:

YOUR ITEM:
• Name: {user_item.name}
• Category: {user_item.get_category_display()}
• Location: {user_item.location}
• Date: {user_item.date}

POTENTIAL MATCH:
• Name: {matched_item.name}
• Category: {matched_item.get_category_display()}
• Location: {matched_item.location}
• Date: {matched_item.date}
• Match Score: {score}%

NEXT STEPS:
1. Review the match details: http://127.0.0.1:8000/items/{matched_item.id}/
2. If this looks like your item, click "Claim This Item"
3. The owner will be notified and can approve your claim

Don't wait - someone else might claim it first!

Best regards,
Lost and Found Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except:
            # Email sending failed, but continue processing
            pass

    def send_reminder_notifications(self):
        """Send reminder notifications for unclaimed items"""
        self.stdout.write("\n⏰ Sending Reminder Notifications...")

        # Get items older than 3 days
        cutoff_date = timezone.now() - timedelta(days=3)
        old_items = Item.objects.filter(status='approved')

        # Get claimed item IDs
        claimed_item_ids = set()
        for claim in Claim.objects.all():
            claimed_item_ids.add(claim.item.id)

        # Filter items without claims
        unclaimed_items = []
        for item in old_items:
            if item.created_at <= cutoff_date and item.id not in claimed_item_ids:
                unclaimed_items.append(item)

        reminders_sent = 0

        for item in unclaimed_items[:10]:  # Limit to 10 per run
            self.send_reminder_email(item)
            reminders_sent += 1

        self.stdout.write(f"⏰ Sent {reminders_sent} reminder notifications")

    def send_reminder_email(self, item):
        """Send reminder email about unclaimed item"""
        subject = f"📢 Reminder: Your {item.get_item_type_display()} Item Needs Attention"
        
        message = f"""
Hi {item.user.username},

Your {item.get_item_type_display().lower()} item hasn't received any claims yet:

ITEM DETAILS:
• Name: {item.name}
• Category: {item.get_category_display()}
• Location: {item.location}
• Date: {item.date}

SUGGESTIONS TO INCREASE SUCCESS:
1. Add more details to the description
2. Upload a photo if you haven't already
3. Share the link with friends: http://127.0.0.1:8000/items/{item.id}/
4. Check if there are similar items you can claim

Keep checking back - new items are added daily!

Best regards,
Lost and Found Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [item.user.email],
                fail_silently=True,
            )
        except:
            pass

    def update_success_metrics(self):
        """Update success rate metrics"""
        self.stdout.write("\n📊 Updating Success Metrics...")
        
        # Calculate current success rates
        total_lost = Item.objects.filter(item_type='lost').count()
        returned_items = Item.objects.filter(status='returned').count()
        claimed_items = Item.objects.filter(status='claimed').count()
        
        success_rate = 0
        if total_lost > 0:
            success_rate = round(((returned_items + claimed_items) / total_lost) * 100, 1)
        
        # Calculate match success rate
        total_matches = ItemMatch.objects.count()
        successful_matches = ItemMatch.objects.filter(
            Q(lost_item__status='claimed') | Q(lost_item__status='returned') |
            Q(found_item__status='claimed') | Q(found_item__status='returned')
        ).count()
        
        match_success_rate = 0
        if total_matches > 0:
            match_success_rate = round((successful_matches / total_matches) * 100, 1)
        
        self.stdout.write(f"📈 Overall Success Rate: {success_rate}%")
        self.stdout.write(f"🎯 Match Success Rate: {match_success_rate}%")
        self.stdout.write(f"📊 Total Items: {Item.objects.count()}")
        self.stdout.write(f"🔄 Total Matches: {total_matches}")
        self.stdout.write(f"✅ Successful Returns: {returned_items}")
        self.stdout.write(f"🎯 Items Claimed: {claimed_items}")
