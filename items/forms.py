from django import forms
from .models import Item, Claim
from django.utils import timezone

class DateInput(forms.DateInput):
    input_type = 'date'

class ItemForm(forms.ModelForm):
    """Form for creating and updating items"""
    class Meta:
        model = Item
        fields = ['name', 'category', 'description', 'location', 'date', 'image', 'contact_info']
        widgets = {
            'date': DateInput(),
            'description': forms.Textarea(attrs={'rows': 4}),
            'location': forms.TextInput(attrs={
                'placeholder': 'e.g., Main Library - 2nd Floor, Study Area Near Windows',
                'maxlength': 200,
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the default date to today
        if not self.initial.get('date'):
            self.initial['date'] = timezone.now().date()

        # Add Bootstrap classes and enhance location field
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        # Enhanced location field
        self.fields['location'].help_text = 'Be as specific as possible - include building, floor, room number, and nearby landmarks'
        self.fields['location'].widget.attrs.update({
            'placeholder': 'e.g., Main Library - 2nd Floor, Study Area Near Windows',
            'maxlength': 200,
            'style': 'font-weight: 500;'
        })

class LostItemForm(ItemForm):
    """Form for creating lost items"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['item_type'] = 'lost'
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.item_type = 'lost'
        if commit:
            instance.save()
        return instance

class FoundItemForm(ItemForm):
    """Form for creating found items"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['item_type'] = 'found'
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.item_type = 'found'
        if commit:
            instance.save()
        return instance

class ClaimForm(forms.ModelForm):
    """Form for claiming items"""
    class Meta:
        model = Claim
        fields = []  # No fields needed as we'll set the item and user in the view

class ItemSearchForm(forms.Form):
    """Form for searching items"""
    search = forms.CharField(required=False, label='Search')
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories')] + Item._meta.get_field('category').choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=DateInput(attrs={'class': 'form-control'}),
        label='Date From'
    )
    date_to = forms.DateField(
        required=False,
        widget=DateInput(attrs={'class': 'form-control'}),
        label='Date To'
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Location'
    )
    item_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + Item._meta.get_field('item_type').choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        self.fields['search'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Search items...'})
