from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.

class User(AbstractUser):

    ROLE_CHOICES = (

        ('user', 'user'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user", null=True, blank=True)

    
    phone = models.CharField(max_length=10, null=True, blank=True)
    


class Expense(models.Model):
    
    PAYMENT_CHOICES = (
        (None, 'Select'),
        ('card', 'Card'),
        ('cash', 'Cash'),
        ('upi', 'UPI')
    )
    
    CATEGORY_CHOICES = (
        (None, 'Select'),
        ('Food', 'Food'),
        ('Travel', 'Travel'),
        ('Entertainment', 'Entertainment'),
        ('Health Care', 'Health Care'),
        ('Housing', 'Housing'),
        ('Transportation', 'Transportation'),
        ('Education', 'Education'),
        ('Personal Care', 'Personal Care'),
        ('Debt Payments', 'Debt Payments'),
        ('Savings & Investments', 'Savings & Investments'),
        ('Gifts & Donations', 'Gifts & Donations'),
        ('Insurance', 'Insurance'),
        ('Miscellaneous', 'Miscellaneous'),
    )
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='Select', null=False, blank=False)
    amount = models.FloatField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='Select', null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    
    def __str__(self):
        return self.title
    


class MonthlyTarget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.IntegerField(validators=[MinValueValidator(1)])  # 1-12
    year = models.IntegerField(validators=[MinValueValidator(2020)])
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    category = models.CharField(max_length=100, choices=Expense.CATEGORY_CHOICES, null=True, blank=True)  # Optional: category-specific target
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'month', 'year', 'category']
    
    def __str__(self):
        category_str = f" - {self.category}" if self.category else ""
        return f"{self.user.username} - {self.year}/{self.month:02d}{category_str} - ${self.target_amount}"


class WeeklyTarget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    week_start_date = models.DateField()  # Monday of the week
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    category = models.CharField(max_length=100, choices=Expense.CATEGORY_CHOICES, null=True, blank=True)  # Optional: category-specific target
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'week_start_date', 'category']
    
    def __str__(self):
        category_str = f" - {self.category}" if self.category else ""
        return f"{self.user.username} - Week of {self.week_start_date}{category_str} - ${self.target_amount}"


class YearlyTarget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField(validators=[MinValueValidator(2020)])
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    category = models.CharField(max_length=100, choices=Expense.CATEGORY_CHOICES, null=True, blank=True)  # Optional: category-specific target
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'year', 'category']
    
    def __str__(self):
        category_str = f" - {self.category}" if self.category else ""
        return f"{self.user.username} - {self.year}{category_str} - ${self.target_amount}"
