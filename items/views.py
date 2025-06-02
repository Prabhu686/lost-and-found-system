from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .models import Item, Claim, ItemMatch
from .forms import LostItemForm, FoundItemForm, ClaimForm, ItemSearchForm
from django.http import HttpResponseForbidden, JsonResponse

def home(request):
    """Home page view"""
    # Get latest lost and found items
    lost_items = Item.objects.filter(item_type='lost', status='approved').order_by('-created_at')[:5]
    found_items = Item.objects.filter(item_type='found', status='approved').order_by('-created_at')[:5]

    context = {
        'lost_items': lost_items,
        'found_items': found_items,
    }
    return render(request, 'items/home.html', context)

def item_list(request):
    """View for listing all items with search and filter - Enhanced with smart search"""
    form = ItemSearchForm(request.GET)
    items = Item.objects.filter(status='approved')
    search_performed = False
    original_count = items.count()

    # Apply filters if form is valid
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        location = form.cleaned_data.get('location')
        item_type = form.cleaned_data.get('item_type')

        # Track if any search was performed
        if any([search, category, date_from, date_to, location, item_type]):
            search_performed = True

        # Enhanced search logic - more flexible and forgiving
        if search:
            # Split search terms for better matching
            search_terms = search.lower().split()
            search_query = Q()

            for term in search_terms:
                search_query |= (
                    Q(name__icontains=term) |
                    Q(description__icontains=term) |
                    Q(location__icontains=term) |
                    Q(category__icontains=term) |
                    Q(contact_info__icontains=term)
                )

            items = items.filter(search_query)

        if category:
            items = items.filter(category=category)

        if date_from:
            items = items.filter(date__gte=date_from)

        if date_to:
            items = items.filter(date__lte=date_to)

        if location:
            items = items.filter(location__icontains=location)

        if item_type:
            items = items.filter(item_type=item_type)

    # Order by relevance if search was performed, otherwise by date
    items = items.order_by('-created_at')

    # If search was performed but no results found, try to find related items
    if search_performed and items.count() == 0:
        items = find_related_items(request.GET, original_count)

    # Paginate results
    paginator = Paginator(items, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'page_obj': page_obj,
        'search_performed': search_performed,
        'total_items': original_count,
    }
    return render(request, 'items/item_list.html', context)

def find_related_items(search_params, original_count):
    """Find related items when exact search returns no results"""
    items = Item.objects.filter(status='approved')

    search = search_params.get('search', '')
    category = search_params.get('category', '')
    location = search_params.get('location', '')
    item_type = search_params.get('item_type', '')

    # Try progressively broader searches
    if search:
        # First try: partial word matches (more aggressive)
        search_terms = search.lower().split()
        related_query = Q()

        for term in search_terms:
            if len(term) > 2:  # Only search terms longer than 2 characters
                related_query |= (
                    Q(name__icontains=term) |
                    Q(description__icontains=term) |
                    Q(location__icontains=term)
                )

        if related_query:
            related_items = items.filter(related_query)
            if related_items.exists():
                return related_items

        # Second try: similar categories based on search terms (enhanced)
        category_keywords = {
            'phone': 'electronics', 'mobile': 'electronics', 'laptop': 'electronics',
            'computer': 'electronics', 'tablet': 'electronics', 'iphone': 'electronics',
            'samsung': 'electronics', 'apple': 'electronics', 'android': 'electronics',
            'airpods': 'electronics', 'headphones': 'electronics', 'earbuds': 'electronics',
            'charger': 'electronics', 'cable': 'electronics', 'mouse': 'electronics',
            'keyboard': 'electronics', 'speaker': 'electronics', 'camera': 'electronics',
            'shirt': 'clothing', 'jacket': 'clothing', 'pants': 'clothing',
            'shoes': 'clothing', 'dress': 'clothing', 'hoodie': 'clothing',
            'jeans': 'clothing', 'sweater': 'clothing', 'coat': 'clothing',
            'watch': 'accessories', 'glasses': 'accessories', 'jewelry': 'accessories',
            'ring': 'accessories', 'necklace': 'accessories', 'bracelet': 'accessories',
            'wallet': 'accessories', 'sunglasses': 'accessories', 'hat': 'accessories',
            'purse': 'bags', 'backpack': 'bags', 'bag': 'bags', 'luggage': 'bags',
            'suitcase': 'bags', 'briefcase': 'bags', 'handbag': 'bags',
            'key': 'keys', 'keys': 'keys', 'keychain': 'keys', 'fob': 'keys',
            'id': 'documents', 'passport': 'documents', 'license': 'documents',
            'card': 'documents', 'certificate': 'documents', 'paper': 'documents'
        }

        for keyword, cat in category_keywords.items():
            if keyword in search.lower():
                cat_items = items.filter(category=cat)
                if cat_items.exists():
                    return cat_items

        # Third try: fuzzy matching for common misspellings and variations
        fuzzy_matches = {
            'iphone': ['phone', 'apple', 'mobile'],
            'airpod': ['earbuds', 'headphones', 'apple'],
            'samsung': ['phone', 'galaxy', 'mobile'],
            'macbook': ['laptop', 'apple', 'computer'],
            'ipad': ['tablet', 'apple'],
            'backpack': ['bag', 'school'],
            'wallet': ['money', 'cards'],
            'glasses': ['eyewear', 'prescription'],
            'keys': ['key', 'car', 'house', 'dorm']
        }

        for main_term, related_terms in fuzzy_matches.items():
            if main_term in search.lower():
                fuzzy_query = Q()
                for related_term in related_terms:
                    fuzzy_query |= (
                        Q(name__icontains=related_term) |
                        Q(description__icontains=related_term)
                    )
                fuzzy_items = items.filter(fuzzy_query)
                if fuzzy_items.exists():
                    return fuzzy_items

    # Fourth try: same category if category filter was used
    if category:
        cat_items = items.filter(category=category)
        if cat_items.exists():
            return cat_items

    # Fifth try: same location area (more flexible)
    if location:
        location_terms = location.lower().split()
        location_query = Q()
        for term in location_terms:
            if len(term) > 2:
                location_query |= Q(location__icontains=term)

        if location_query:
            location_items = items.filter(location_query)
            if location_items.exists():
                return location_items

    # Sixth try: same item type
    if item_type:
        type_items = items.filter(item_type=item_type)
        if type_items.exists():
            return type_items

    # Seventh try: return recent items from popular categories
    popular_categories = ['electronics', 'bags', 'keys', 'accessories', 'clothing', 'documents']
    for cat in popular_categories:
        cat_items = items.filter(category=cat)
        if cat_items.exists():
            return cat_items

    # If all else fails, return recent items (always return something)
    return items

def item_detail(request, pk):
    """View for item details"""
    item = get_object_or_404(Item, pk=pk, status='approved')

    # Check if user can claim this item
    can_claim = False
    if request.user.is_authenticated:
        # User can claim found items if they have reported a lost item
        if item.item_type == 'found' and Item.objects.filter(user=request.user, item_type='lost').exists():
            can_claim = True
        # User can claim lost items if they have reported a found item
        elif item.item_type == 'lost' and Item.objects.filter(user=request.user, item_type='found').exists():
            can_claim = True

    # Get potential matches
    matches = None
    if item.item_type == 'lost':
        matches = ItemMatch.objects.filter(lost_item=item).order_by('-match_score')[:5]
    else:
        matches = ItemMatch.objects.filter(found_item=item).order_by('-match_score')[:5]

    # Get similar items (same category, different type)
    similar_items_query = Item.objects.filter(
        category=item.category,
        status='approved'
    ).exclude(
        id=item.id
    )
    if request.user.is_authenticated:
        similar_items_query = similar_items_query.exclude(user=request.user)

    similar_items = list(similar_items_query[:6])

    # Get exact related items (same keywords in name/description)
    item_keywords = item.name.lower().split() + item.description.lower().split()
    exact_related = []

    for keyword in item_keywords:
        if len(keyword) > 3 and len(exact_related) < 4:  # Only consider words longer than 3 characters
            related_query = Item.objects.filter(
                Q(name__icontains=keyword) | Q(description__icontains=keyword),
                status='approved'
            ).exclude(
                id=item.id
            )
            if request.user.is_authenticated:
                related_query = related_query.exclude(user=request.user)

            related_items = list(related_query[:3])

            for rel_item in related_items:
                if rel_item not in exact_related and len(exact_related) < 4:
                    exact_related.append(rel_item)

    context = {
        'item': item,
        'can_claim': can_claim,
        'matches': matches,
        'similar_items': similar_items,
        'exact_related': exact_related,
    }
    return render(request, 'items/item_detail.html', context)

@login_required
def report_lost_item(request):
    """View for reporting a lost item"""
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()

            # Find potential matches
            find_matches(item)

            messages.success(request, 'Your lost item has been reported and is pending approval.')
            return redirect('dashboard')
    else:
        form = LostItemForm()

    context = {
        'form': form,
        'title': 'Report Lost Item',
    }
    return render(request, 'items/item_form.html', context)

@login_required
def report_found_item(request):
    """View for reporting a found item"""
    if request.method == 'POST':
        form = FoundItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()

            # Find potential matches
            find_matches(item)

            messages.success(request, 'Your found item has been reported and is pending approval.')
            return redirect('dashboard')
    else:
        form = FoundItemForm()

    context = {
        'form': form,
        'title': 'Report Found Item',
    }
    return render(request, 'items/item_form.html', context)

@login_required
def claim_item(request, pk):
    """View for claiming an item"""
    item = get_object_or_404(Item, pk=pk, status='approved')

    # Check if user can claim this item
    if item.user == request.user:
        messages.error(request, 'You cannot claim your own item.')
        return redirect('item_detail', pk=pk)

    if request.method == 'POST':
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.item = item
            claim.claimed_by = request.user
            claim.save()

            messages.success(request, 'Your claim has been submitted and is pending approval.')
            return redirect('dashboard')
    else:
        form = ClaimForm()

    context = {
        'form': form,
        'item': item,
    }
    return render(request, 'items/claim_form.html', context)

@login_required
def dashboard(request):
    """User dashboard view"""
    # Get user's items
    user_items = Item.objects.filter(user=request.user).order_by('-created_at')

    # Get user's claims
    user_claims = Claim.objects.filter(claimed_by=request.user).order_by('-claim_date')

    # Get claims on user's items
    item_claims = Claim.objects.filter(item__user=request.user).order_by('-claim_date')

    context = {
        'user_items': user_items,
        'user_claims': user_claims,
        'item_claims': item_claims,
    }
    return render(request, 'items/dashboard.html', context)

@login_required
def update_item(request, pk):
    """View for updating an item"""
    item = get_object_or_404(Item, pk=pk, user=request.user)

    if item.item_type == 'lost':
        form_class = LostItemForm
    else:
        form_class = FoundItemForm

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your item has been updated.')
            return redirect('dashboard')
    else:
        form = form_class(instance=item)

    context = {
        'form': form,
        'title': f'Update {item.get_item_type_display()} Item',
    }
    return render(request, 'items/item_form.html', context)

@login_required
def delete_item(request, pk):
    """View for deleting an item"""
    item = get_object_or_404(Item, pk=pk, user=request.user)

    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Your item has been deleted.')
        return redirect('dashboard')

    context = {
        'item': item,
    }
    return render(request, 'items/item_confirm_delete.html', context)

@login_required
def approve_claim(request, pk):
    """View for approving a claim"""
    claim = get_object_or_404(Claim, pk=pk, item__user=request.user)

    if request.method == 'POST':
        claim.approved = True
        claim.save()

        # Update item status
        item = claim.item
        item.status = 'claimed'
        item.save()

        messages.success(request, 'The claim has been approved.')
        return redirect('dashboard')

    context = {
        'claim': claim,
    }
    return render(request, 'items/claim_approve.html', context)

@login_required
def reject_claim(request, pk):
    """View for rejecting a claim"""
    claim = get_object_or_404(Claim, pk=pk, item__user=request.user)

    if request.method == 'POST':
        claim.delete()
        messages.success(request, 'The claim has been rejected.')
        return redirect('dashboard')

    context = {
        'claim': claim,
    }
    return render(request, 'items/claim_reject.html', context)

@login_required
def mark_returned(request, pk):
    """View for marking an item as returned"""
    item = get_object_or_404(Item, pk=pk)

    # Check if user is the owner or the claimer
    is_owner = item.user == request.user
    is_claimer = Claim.objects.filter(item=item, claimed_by=request.user, approved=True).exists()

    if not (is_owner or is_claimer):
        return HttpResponseForbidden("You don't have permission to mark this item as returned.")

    if request.method == 'POST':
        item.status = 'returned'
        item.save()
        messages.success(request, 'The item has been marked as returned.')
        return redirect('dashboard')

    context = {
        'item': item,
    }
    return render(request, 'items/item_return.html', context)

# Helper function to find potential matches
def find_matches(item):
    """Find potential matches for a lost or found item"""
    if item.item_type == 'lost':
        # Find matching found items
        potential_matches = Item.objects.filter(
            item_type='found',
            status='approved',
            category=item.category
        )

        for match in potential_matches:
            # Calculate a simple match score based on text similarity
            # This is a very basic implementation - in a real app, you'd use more sophisticated matching
            name_match = 1 if item.name.lower() in match.name.lower() or match.name.lower() in item.name.lower() else 0
            desc_match = 1 if item.description.lower() in match.description.lower() or match.description.lower() in item.description.lower() else 0
            location_match = 1 if item.location.lower() in match.location.lower() or match.location.lower() in item.location.lower() else 0

            # Date proximity (0-1 score)
            date_diff = abs((item.date - match.date).days)
            date_score = 1 if date_diff == 0 else max(0, 1 - (date_diff / 30))  # Within a month

            # Calculate overall score (0-4)
            score = name_match + desc_match + location_match + date_score

            # Only create a match if score is above threshold
            if score > 1:
                ItemMatch.objects.create(
                    lost_item=item,
                    found_item=match,
                    match_score=score
                )

    elif item.item_type == 'found':
        # Find matching lost items
        potential_matches = Item.objects.filter(
            item_type='lost',
            status='approved',
            category=item.category
        )

        for match in potential_matches:
            # Calculate match score (same as above)
            name_match = 1 if item.name.lower() in match.name.lower() or match.name.lower() in item.name.lower() else 0
            desc_match = 1 if item.description.lower() in match.description.lower() or match.description.lower() in item.description.lower() else 0
            location_match = 1 if item.location.lower() in match.location.lower() or match.location.lower() in item.location.lower() else 0

            date_diff = abs((item.date - match.date).days)
            date_score = 1 if date_diff == 0 else max(0, 1 - (date_diff / 30))

            score = name_match + desc_match + location_match + date_score

            if score > 1:
                ItemMatch.objects.create(
                    lost_item=match,
                    found_item=item,
                    match_score=score
                )

def statistics(request):
    """View for displaying statistics and analytics"""
    # Get total counts
    total_items = Item.objects.count()
    total_lost = Item.objects.filter(item_type='lost').count()
    total_found = Item.objects.filter(item_type='found').count()
    total_claimed = Item.objects.filter(status='claimed').count()
    total_returned = Item.objects.filter(status='returned').count()

    # Success rate
    success_rate = 0
    if total_lost > 0:
        success_rate = round((total_returned / total_lost) * 100, 1)

    # Items by category
    categories = Item.objects.values('category').annotate(count=Count('id')).order_by('-count')

    # Items by status
    status_counts = Item.objects.values('status').annotate(count=Count('id')).order_by('-count')

    # Recent activity
    recent_lost = Item.objects.filter(item_type='lost').order_by('-created_at')[:5]
    recent_found = Item.objects.filter(item_type='found').order_by('-created_at')[:5]
    recent_claims = Claim.objects.order_by('-claim_date')[:5]

    # Items by date (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    items_by_date = []

    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        lost_count = Item.objects.filter(item_type='lost', date=date).count()
        found_count = Item.objects.filter(item_type='found', date=date).count()

        items_by_date.append({
            'date': date.strftime('%Y-%m-%d'),
            'lost': lost_count,
            'found': found_count
        })

    # Top locations
    top_locations = Item.objects.values('location').annotate(count=Count('id')).order_by('-count')[:5]

    # Match success rate
    total_matches = ItemMatch.objects.count()
    successful_matches = ItemMatch.objects.filter(
        Q(lost_item__status='claimed') | Q(lost_item__status='returned') |
        Q(found_item__status='claimed') | Q(found_item__status='returned')
    ).count()

    match_success_rate = 0
    if total_matches > 0:
        match_success_rate = round((successful_matches / total_matches) * 100, 1)

    context = {
        'total_items': total_items,
        'total_lost': total_lost,
        'total_found': total_found,
        'total_claimed': total_claimed,
        'total_returned': total_returned,
        'success_rate': success_rate,
        'categories': categories,
        'status_counts': status_counts,
        'recent_lost': recent_lost,
        'recent_found': recent_found,
        'recent_claims': recent_claims,
        'items_by_date': items_by_date,
        'top_locations': top_locations,
        'total_matches': total_matches,
        'successful_matches': successful_matches,
        'match_success_rate': match_success_rate,
    }

    return render(request, 'items/statistics.html', context)

def success_dashboard(request):
    """Enhanced success rate dashboard"""
    from django.db.models import Count, Q
    from datetime import timedelta
    import json

    # Basic metrics
    total_items = Item.objects.count()
    total_lost = Item.objects.filter(item_type='lost').count()
    total_found = Item.objects.filter(item_type='found').count()
    total_claimed = Item.objects.filter(status='claimed').count()
    total_returned = Item.objects.filter(status='returned').count()

    # Success rate calculation
    success_rate = 0
    if total_lost > 0:
        success_rate = round(((total_returned + total_claimed) / total_lost) * 100, 1)

    # Match statistics
    total_matches = ItemMatch.objects.count()
    successful_matches = ItemMatch.objects.filter(
        Q(lost_item__status='claimed') | Q(lost_item__status='returned') |
        Q(found_item__status='claimed') | Q(found_item__status='returned')
    ).count()

    match_success_rate = 0
    if total_matches > 0:
        match_success_rate = round((successful_matches / total_matches) * 100, 1)

    # Success factors
    items_with_images = Item.objects.exclude(image='').count()
    items_with_images_pct = round((items_with_images / max(total_items, 1)) * 100, 1)

    detailed_descriptions = Item.objects.filter(description__regex=r'.{50,}').count()
    detailed_descriptions_pct = round((detailed_descriptions / max(total_items, 1)) * 100, 1)

    specific_locations = Item.objects.filter(location__regex=r'.{20,}').count()
    specific_locations_pct = round((specific_locations / max(total_items, 1)) * 100, 1)

    quick_reports = Item.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=1)
    ).count()
    quick_reports_pct = round((quick_reports / max(total_items, 1)) * 100, 1)

    # Category success rates
    categories = ['electronics', 'clothing', 'accessories', 'documents', 'keys', 'bags', 'other']
    category_success = []

    for category in categories:
        cat_lost = Item.objects.filter(category=category, item_type='lost').count()
        cat_success = Item.objects.filter(
            category=category,
            status__in=['claimed', 'returned']
        ).count()

        rate = 0
        if cat_lost > 0:
            rate = round((cat_success / cat_lost) * 100, 1)

        category_success.append({
            'name': category.title(),
            'rate': rate
        })

    # Recent matches
    recent_matches = ItemMatch.objects.select_related('lost_item', 'found_item').order_by('-created_at')[:10]

    # Chart data for last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    chart_labels = []
    chart_data = []

    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        chart_labels.append(date.strftime('%m/%d'))

        # Calculate success rate for this day
        day_lost = Item.objects.filter(
            item_type='lost',
            created_at__date=date.date()
        ).count()

        day_success = Item.objects.filter(
            status__in=['claimed', 'returned'],
            created_at__date=date.date()
        ).count()

        day_rate = 0
        if day_lost > 0:
            day_rate = round((day_success / day_lost) * 100, 1)

        chart_data.append(day_rate)

    context = {
        'success_rate': success_rate,
        'total_returned': total_returned,
        'total_matches': total_matches,
        'match_success_rate': match_success_rate,
        'items_with_images': items_with_images_pct,
        'detailed_descriptions': detailed_descriptions_pct,
        'specific_locations': specific_locations_pct,
        'quick_reports': quick_reports_pct,
        'category_success': category_success,
        'recent_matches': recent_matches,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }

    return render(request, 'items/success_dashboard.html', context)

def api_items_by_date(request):
    """API endpoint for items by date (for charts)"""
    days = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)

    items_by_date = []

    for i in range(days):
        date = start_date + timedelta(days=i)
        lost_count = Item.objects.filter(item_type='lost', date=date).count()
        found_count = Item.objects.filter(item_type='found', date=date).count()

        items_by_date.append({
            'date': date.strftime('%Y-%m-%d'),
            'lost': lost_count,
            'found': found_count
        })

    return JsonResponse({'data': items_by_date})

def share_item(request, pk):
    """View for sharing an item on social media"""
    item = get_object_or_404(Item, pk=pk)

    context = {
        'item': item,
    }

    return render(request, 'items/social_share.html', context)

def select_location(request):
    """View for selecting a location on a map"""
    form_action = request.GET.get('form_action', '')
    cancel_url = request.GET.get('cancel_url', '')

    context = {
        'form_action': form_action,
        'cancel_url': cancel_url,
    }

    return render(request, 'items/map_location.html', context)
