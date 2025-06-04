from django import forms
from django.contrib.auth.forms import UserCreationForm
from expense.models import User, Expense

# user register form
class SignUpForm(UserCreationForm):
    
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control mb-3', 'placeholder':'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control mb-3', 'placeholder':'Confirm Password'}))
    
    class Meta:
        
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone']
        
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control mb-3', 'placeholder':'Username'}),
            'email': forms.EmailInput(attrs={'class':'form-control mb-3', 'placeholder':'Email Address'}),
            'phone': forms.TextInput(attrs={'class':'form-control mb-3', 'placeholder':'Phone Number'})
        }
    
    
class SignInForm(forms.Form):
    
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control mb-3'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control mb-3'}))
    
    
class ExpenseForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(ExpenseForm, self).__init__(*args, **kwargs)
    
    class Meta:
        
        model = Expense
        fields = ['title', 'category', 'amount', 'payment_method']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder':'Enter title'}),
            'category': forms.Select(attrs={'class': 'form-control form-select mb-3', 'placeholder':'Enter carogory'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control mb-3', 'placeholder':'Enter amount'}),
            'payment_method': forms.Select(attrs={'class': 'form-control form-select mb-3'})
        }
        
        labels = {
            'title': '',
            'category': '',
            'amount': '',
            'payment_method': 'Select Payment Method'
        }
        
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    """Form for updating basic user profile information."""
    first_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    

    
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., +1 (555) 123-4567'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        # Add or remove fields based on your User model
    
    def clean_email(self):
        """Validate that the email is not already in use by another user."""
        email = self.cleaned_data.get('email')
        username = self.instance.username
        
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('This email address is already in use.')
        
        return email


class PasswordChangeForm(DjangoPasswordChangeForm):
    """Enhanced form for changing user password with Bootstrap styling."""
    
    error_messages = {
        'password_incorrect': "Your current password was entered incorrectly. Please enter it again.",
        'password_mismatch': "The two password fields didn't match.",
    }
    
    old_password = forms.CharField(
        label="Current Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password',
        }),
    )
    
    new_password1 = forms.CharField(
        label="New Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
        }),
        help_text="Your password must be at least 8 characters long and contain a mix of letters, numbers, and symbols."
    )
    
    new_password2 = forms.CharField(
        label="Confirm New Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
        }),
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can customize field order or other attributes here
    """Custom form for changing password with Bootstrap styling."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap CSS classes to all fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
            
    old_password = forms.CharField(
        label="Current Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'class': 'form-control',
        }),
    )
    
    new_password1 = forms.CharField(
        label="New Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
        }),
    )
    
    new_password2 = forms.CharField(
        label="Confirm New Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
        }),
    )



from django import forms
from django.core.validators import MinValueValidator
from decimal import Decimal
import datetime
from .models import MonthlyTarget, WeeklyTarget, YearlyTarget, Expense


class MonthlyTargetForm(forms.ModelForm):
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    
    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    year = forms.IntegerField(
        min_value=2020,
        max_value=2030,
        initial=datetime.datetime.now().year,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    target_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        })
    )
    
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + list(Expense.CATEGORY_CHOICES)[1:],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = MonthlyTarget
        fields = ['month', 'year', 'target_amount', 'category']
    
    def clean(self):
        cleaned_data = super().clean()
        month = cleaned_data.get('month')
        year = cleaned_data.get('year')
        category = cleaned_data.get('category') or None
        
        if month and year:
            # Check if target already exists for this month/year/category combination
            existing = MonthlyTarget.objects.filter(
                user=self.instance.user if hasattr(self.instance, 'user') else None,
                month=month,
                year=year,
                category=category
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                category_str = f" for {category}" if category else ""
                raise forms.ValidationError(
                    f"A target already exists for {dict(self.MONTH_CHOICES)[int(month)]} {year}{category_str}."
                )
        
        return cleaned_data


class WeeklyTargetForm(forms.ModelForm):
    week_start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text="Select any date in the week (will be adjusted to Monday)"
    )
    
    target_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        })
    )
    
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + list(Expense.CATEGORY_CHOICES)[1:],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = WeeklyTarget
        fields = ['week_start_date', 'target_amount', 'category']
    
    def clean_week_start_date(self):
        date = self.cleaned_data['week_start_date']
        # Convert to Monday of that week
        monday = date - datetime.timedelta(days=date.weekday())
        return monday
    
    def clean(self):
        cleaned_data = super().clean()
        week_start_date = cleaned_data.get('week_start_date')
        category = cleaned_data.get('category') or None
        
        if week_start_date:
            # Check if target already exists for this week/category combination
            existing = WeeklyTarget.objects.filter(
                user=self.instance.user if hasattr(self.instance, 'user') else None,
                week_start_date=week_start_date,
                category=category
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                category_str = f" for {category}" if category else ""
                raise forms.ValidationError(
                    f"A target already exists for the week of {week_start_date}{category_str}."
                )
        
        return cleaned_data


class YearlyTargetForm(forms.ModelForm):
    year = forms.IntegerField(
        min_value=2020,
        max_value=2030,
        initial=datetime.datetime.now().year,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    target_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        })
    )
    
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + list(Expense.CATEGORY_CHOICES)[1:],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = YearlyTarget
        fields = ['year', 'target_amount', 'category']
    
    def clean(self):
        cleaned_data = super().clean()
        year = cleaned_data.get('year')
        category = cleaned_data.get('category') or None
        
        if year:
            # Check if target already exists for this year/category combination
            existing = YearlyTarget.objects.filter(
                user=self.instance.user if hasattr(self.instance, 'user') else None,
                year=year,
                category=category
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                category_str = f" for {category}" if category else ""
                raise forms.ValidationError(
                    f"A target already exists for {year}{category_str}."
                )
        
        return cleaned_data
