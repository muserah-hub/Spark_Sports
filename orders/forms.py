from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    """
    Form to collect customer shipping details during checkout.
    """
    PROVINCE_CHOICES = (
        ('', 'Select Province'),
        ('Punjab', 'Punjab'),
        ('Sindh', 'Sindh'),
        ('Khyber Pakhtunkhwa', 'Khyber Pakhtunkhwa'),
        ('Balochistan', 'Balochistan'),
        ('Gilgit-Baltistan', 'Gilgit-Baltistan'),
        ('Azad Jammu & Kashmir', 'Azad Jammu & Kashmir'),
        ('Islamabad Capital Territory', 'Islamabad Capital Territory'),
    )

    province = forms.ChoiceField(choices=PROVINCE_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone', 
            'address', 'city', 'province', 'postal_code'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone (e.g. 03001234567)'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'House #, Street Address, Area'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City (e.g. Lahore, Karachi)'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
        }
