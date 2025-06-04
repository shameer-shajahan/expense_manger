from django.shortcuts import render, redirect
from django.views.generic import View
from expense.forms import SignUpForm, SignInForm, ExpenseForm
from django.contrib.auth import authenticate, login, logout
from expense.models import Expense, User
from expense.decorators import signin_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.views import View
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncYear, TruncDay
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta, datetime
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.urls import reverse_lazy
from .forms import UserProfileForm, PasswordChangeForm
User = get_user_model()
from django.views import View
from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth, TruncDay, TruncYear

# Import for PDF generation
from xhtml2pdf import pisa
from io import BytesIO
from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import timedelta
from django.utils.decorators import method_decorator
# Create your views here.

decorators = [signin_required, never_cache]

class HomeView(View):
    
    template_name = 'home.html'
    
    def get(self, request, *args, **kwargs):
        
        return render(request, self.template_name)

@method_decorator(never_cache, name='dispatch')
class SignUpView(View):
    
    template_name = 'register.html'
    form_class = SignUpForm
    
    def get(self, request, *args, **kwargs):
        
        form = self.form_class()
        
        return render(request, self.template_name, {'form':form, 'action':'Signup'})
    
    def post(self, request, *args, **kwargs):
        
        form_data = request.POST
        form = self.form_class(form_data)
        
        if form.is_valid():
            
            form.save()
            return redirect('signin')
        
        return render(request, self.template_name, {'form':form, 'action':'Signup'})

@method_decorator(never_cache, name='dispatch')
class SignInView(View):
    
    template_name = 'login.html'
    form_class = SignInForm
    
    def get(self, request, *args, **kwargs):
        
        form = self.form_class()
        
        return render(request, self.template_name, {'form':form, 'action':'Signin'})

    def post(self, request, *args, **kwargs):
        
        form_data = request.POST
        form = self.form_class(form_data)
        
        if form.is_valid():
            
            data = form.cleaned_data
                    
            uname = data.get('username')
            pwd = data.get('password')
        
            user_obj = authenticate(request, username=uname, password=pwd)
            
            if user_obj:
                
                login(request, user_obj)
                
                # Check user role and redirect accordingly
                if user_obj.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('expense-summary')
        
        return render(request, self.template_name, {'form':form, 'action':'Signin'})

@method_decorator(decorators, name='dispatch')
class SignOutView(View):
    
    def get(self, request, *args, **kwargs):
        
        logout(request)
        return redirect('home')
 
@method_decorator(decorators, name='dispatch')       
class indexView(View):
    
    template_name = 'index.html'
    form_class = ExpenseForm
    
    def get(self, request, *args, **kwargs):
        
        qs = Expense.objects.filter(owner=request.user)
        
        form = self.form_class()
        
        return render(request, self.template_name, {'form':form, 'data':qs})
    
    def post(self, request, *args, **kwargs):
        
        form_data = request.POST
        form = self.form_class(form_data)

        if form.is_valid():
            
            form.instance.owner = request.user
            form.save()
            return redirect('index')
        
        return render(request, self.template_name, {'form':form})

@method_decorator(decorators, name='dispatch')   
class ExpenceDeleteView(View):
    
    def get(self, request, *args, **kwargs):
        
        id = kwargs.get('pk')
        Expense.objects.get(id=id).delete()
        return redirect('index')
    
@method_decorator(decorators, name='dispatch')
class ExpenseUpdateView(View):
    
    template_name = 'update.html'
    form_class = ExpenseForm
    
    def get(self, request, *args, **kwargs):
        
        id = kwargs.get('pk')
        expense_obj = Expense.objects.get(id=id)
        form = self.form_class(instance=expense_obj)
        
        return render(request, self.template_name, {'form':form})

    def post(self, request, *args, **kwargs):
        
        form_data = request.POST
        id = kwargs.get('pk')
        expense_obj = Expense.objects.get(id=id)
        
        form = self.form_class(form_data, instance=expense_obj)
        
        if form.is_valid():
            
            form.instance.owner = request.user
            form.save()
            return redirect('index')
        
        return render(request, self.template_name, {'form':form})





from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncDay, TruncYear
from datetime import timedelta, date
from decimal import Decimal
from .models import Expense, MonthlyTarget, WeeklyTarget, YearlyTarget

@method_decorator(decorators, name='dispatch')
class ExpenseSummaryView(View):
    
    template_name = 'expense_summary.html'

    def get_week_start_date(self, target_date):
        """Get the Monday of the week for a given date"""
        days_since_monday = target_date.weekday()
        return target_date - timedelta(days=days_since_monday)

    def calculate_target_progress(self, current_expense, target_amount):
        """Calculate progress towards target and remaining amount"""
        if not target_amount:
            return {
                'progress_percentage': 0,
                'remaining_amount': 0,
                'status': 'no_target',
                'over_budget': False,
                'excess_amount': 0
            }
        
        # Convert to Decimal for precise calculations
        current_expense = Decimal(str(current_expense))
        target_amount = Decimal(str(target_amount))
        
        progress_percentage = (current_expense / target_amount) * 100
        remaining_amount = target_amount - current_expense
        over_budget = current_expense > target_amount
        
        if over_budget:
            status = 'over_budget'
        elif progress_percentage >= 90:
            status = 'near_limit'
        elif progress_percentage >= 75:
            status = 'warning'
        else:
            status = 'on_track'
        
        return {
            'progress_percentage': round(float(progress_percentage), 2),
            'remaining_amount': float(remaining_amount),
            'status': status,
            'over_budget': over_budget,
            'excess_amount': float(current_expense - target_amount) if over_budget else 0
        }

    def get(self, request, *args, **kwargs):
        # Base queryset for all user expenses
        qs = Expense.objects.filter(owner=request.user)
        
        # Get current date and time
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)
        week_start = self.get_week_start_date(today)
       
        # Total expenses
        total_expense = qs.aggregate(total=Sum('amount'))['total'] or 0
        
        # Today's expenses
        today_expense = qs.filter(created_at__date=today).aggregate(total=Sum('amount'))['total'] or 0
        
        # Yesterday's expenses
        yesterday_expense = qs.filter(created_at__date=yesterday).aggregate(total=Sum('amount'))['total'] or 0
        
        # This week's expenses
        weekly_expense = qs.filter(created_at__date__gte=start_of_week).aggregate(total=Sum('amount'))['total'] or 0
        
        # This month's expenses
        monthly_expense = qs.filter(created_at__date__gte=start_of_month).aggregate(total=Sum('amount'))['total'] or 0
        
        # This year's expenses
        yearly_expense = qs.filter(created_at__date__gte=start_of_year).aggregate(total=Sum('amount'))['total'] or 0
        
        # Get targets for current periods
        current_month_target = MonthlyTarget.objects.filter(
            user=request.user,
            month=today.month,
            year=today.year,
            category__isnull=True  # Overall target, not category-specific
        ).first()
        
        current_week_target = WeeklyTarget.objects.filter(
            user=request.user,
            week_start_date=week_start,
            category__isnull=True
        ).first()
        
        current_year_target = YearlyTarget.objects.filter(
            user=request.user,
            year=today.year,
            category__isnull=True
        ).first()
        
        # Calculate target progress
        monthly_target_progress = self.calculate_target_progress(
            monthly_expense, 
            current_month_target.target_amount if current_month_target else None
        )
        
        weekly_target_progress = self.calculate_target_progress(
            weekly_expense, 
            current_week_target.target_amount if current_week_target else None
        )
        
        yearly_target_progress = self.calculate_target_progress(
            yearly_expense, 
            current_year_target.target_amount if current_year_target else None
        )
        
        # Category-wise expenses with targets
        category_expenses = list(qs.values('category').annotate(total=Sum('amount')).order_by('-total'))
        
        # Add target information to category expenses
        for category_expense in category_expenses:
            category_name = category_expense['category']
            
            # Monthly category target
            monthly_cat_target = MonthlyTarget.objects.filter(
                user=request.user,
                month=today.month,
                year=today.year,
                category=category_name
            ).first()
            
            # Weekly category target
            weekly_cat_target = WeeklyTarget.objects.filter(
                user=request.user,
                week_start_date=week_start,
                category=category_name
            ).first()
            
            # Yearly category target
            yearly_cat_target = YearlyTarget.objects.filter(
                user=request.user,
                year=today.year,
                category=category_name
            ).first()
            
            # Calculate category expenses for different periods
            category_monthly_expense = qs.filter(
                category=category_name,
                created_at__date__gte=start_of_month
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            category_weekly_expense = qs.filter(
                category=category_name,
                created_at__date__gte=start_of_week
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            category_yearly_expense = qs.filter(
                category=category_name,
                created_at__date__gte=start_of_year
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            category_expense.update({
                'monthly_target': float(monthly_cat_target.target_amount) if monthly_cat_target else None,
                'weekly_target': float(weekly_cat_target.target_amount) if weekly_cat_target else None,
                'yearly_target': float(yearly_cat_target.target_amount) if yearly_cat_target else None,
                'monthly_expense': category_monthly_expense,
                'weekly_expense': category_weekly_expense,
                'yearly_expense': category_yearly_expense,
                'monthly_progress': self.calculate_target_progress(
                    category_monthly_expense,
                    monthly_cat_target.target_amount if monthly_cat_target else None
                ),
                'weekly_progress': self.calculate_target_progress(
                    category_weekly_expense,
                    weekly_cat_target.target_amount if weekly_cat_target else None
                ),
                'yearly_progress': self.calculate_target_progress(
                    category_yearly_expense,
                    yearly_cat_target.target_amount if yearly_cat_target else None
                )
            })
        
        # Payment method-wise expenses
        payment_expenses = list(qs.values('payment_method').annotate(total=Sum('amount')).order_by('-total'))
        
        # Monthly breakdown for the current year
        current_year = today.year
        monthly_expenses = list(
            qs.filter(created_at__year=current_year)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        
        # Add target information to monthly expenses
        for expense in monthly_expenses:
            if expense['month']:
                expense['month_name'] = expense['month'].strftime('%B')
                month_num = expense['month'].month
                
                # Get monthly target for this month
                month_target = MonthlyTarget.objects.filter(
                    user=request.user,
                    month=month_num,
                    year=current_year,
                    category__isnull=True
                ).first()
                
                expense['target_amount'] = float(month_target.target_amount) if month_target else None
                expense['progress'] = self.calculate_target_progress(
                    expense['total'],
                    month_target.target_amount if month_target else None
                )
        
        # Daily expenses for the last 30 days
        thirty_days_ago = today - timedelta(days=30)
        daily_expenses = list(
            qs.filter(created_at__date__gte=thirty_days_ago)
            .annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(total=Sum('amount'))
            .order_by('day')
        )
        
        # Format days for better display
        for expense in daily_expenses:
            if expense['day']:
                expense['day_formatted'] = expense['day'].strftime('%Y-%m-%d')
                expense['day_name'] = expense['day'].strftime('%a, %b %d')
        
        # Yearly breakdown
        yearly_expenses = list(
            qs.annotate(year=TruncYear('created_at'))
            .values('year')
            .annotate(total=Sum('amount'))
            .order_by('year')
        )
        
        # Add target information to yearly expenses
        for expense in yearly_expenses:
            if expense['year']:
                expense['year_formatted'] = expense['year'].strftime('%Y')
                year_num = expense['year'].year
                
                # Get yearly target for this year
                year_target = YearlyTarget.objects.filter(
                    user=request.user,
                    year=year_num,
                    category__isnull=True
                ).first()
                
                expense['target_amount'] = float(year_target.target_amount) if year_target else None
                expense['progress'] = self.calculate_target_progress(
                    expense['total'],
                    year_target.target_amount if year_target else None
                )
        
        # Extract data for charts
        monthly_expenses_labels = [expense['month_name'] for expense in monthly_expenses if expense['month']]
        monthly_expenses_data = [float(expense['total']) for expense in monthly_expenses if expense['month']]
        monthly_target_data = [expense['target_amount'] if expense['target_amount'] else 0 for expense in monthly_expenses if expense['month']]
        
        daily_expenses_labels = [expense['day_name'] for expense in daily_expenses if expense['day']]
        daily_expenses_data = [float(expense['total']) for expense in daily_expenses if expense['day']]
        
        category_labels = [expense['category'] for expense in category_expenses]
        category_data = [float(expense['total']) for expense in category_expenses]
        
        # Get all targets for display
        all_monthly_targets = MonthlyTarget.objects.filter(
            user=request.user,
            month=today.month,
            year=today.year
        ).order_by('category')
        
        all_weekly_targets = WeeklyTarget.objects.filter(
            user=request.user,
            week_start_date=week_start
        ).order_by('category')
        
        all_yearly_targets = YearlyTarget.objects.filter(
            user=request.user,
            year=today.year
        ).order_by('category')
        
        context = {
            # Summary totals
            'total_expense': total_expense,
            'today_expense': today_expense,
            'yesterday_expense': yesterday_expense,
            'weekly_expense': weekly_expense,
            'monthly_expense': monthly_expense,
            'yearly_expense': yearly_expense,
            
            # Target information
            'current_month_target': current_month_target,
            'current_week_target': current_week_target,
            'current_year_target': current_year_target,
            'monthly_target_progress': monthly_target_progress,
            'weekly_target_progress': weekly_target_progress,
            'yearly_target_progress': yearly_target_progress,
            
            # All targets
            'all_monthly_targets': all_monthly_targets,
            'all_weekly_targets': all_weekly_targets,
            'all_yearly_targets': all_yearly_targets,
            
            # Detailed breakdowns
            'category_expenses': category_expenses,
            'payment_expenses': payment_expenses,
            'monthly_expenses': monthly_expenses,
            'daily_expenses': daily_expenses,
            'yearly_expenses': yearly_expenses,
            
            # Chart data
            'monthly_expenses_labels': monthly_expenses_labels,
            'monthly_expenses_data': monthly_expenses_data,
            'monthly_target_data': monthly_target_data,
            'daily_expenses_labels': daily_expenses_labels,
            'daily_expenses_data': daily_expenses_data,
            'category_labels': category_labels,
            'category_data': category_data,
            
            # Date references
            'today': today,
            'start_of_week': start_of_week,
            'start_of_month': start_of_month,
            'start_of_year': start_of_year,
            'week_start': week_start,
        }
        
        return render(request, self.template_name, context)
    
@method_decorator(decorators, name='dispatch')
class UserProfileView(LoginRequiredMixin, View):
    """Class-based view for displaying and updating user profile and password."""
    template_name = 'profile.html'
    success_url = reverse_lazy('profile')
    
    def get(self, request):
        """Handle GET requests: display user profile with both forms."""
        user = request.user
        profile_form = UserProfileForm(instance=user)
        password_form = PasswordChangeForm(user=user)
        
        context = {
            'profile_form': profile_form,
            'password_form': password_form,
            'user': user,
            'active_tab': request.GET.get('tab', 'profile')  # Default to profile tab
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Handle POST requests: process form data for both profile and password."""
        user = request.user
        active_tab = 'profile'  # Default tab
        
        # Determine which form was submitted
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=user)
            password_form = PasswordChangeForm(user=user)
            
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Your profile has been updated successfully!")
                return redirect(self.success_url)
            else:
                active_tab = 'profile'
                
        elif 'change_password' in request.POST:
            profile_form = UserProfileForm(instance=user)
            password_form = PasswordChangeForm(user=user, data=request.POST)
            
            if password_form.is_valid():
                password_form.save()
                # Important: update the session to prevent logging out
                update_session_auth_hash(request, user)
                messages.success(request, "Your password has been changed successfully!")
                return redirect(self.success_url)
            else:
                active_tab = 'password'
        else:
            # Fallback for unknown submission
            profile_form = UserProfileForm(instance=user)
            password_form = PasswordChangeForm(user=user)
            messages.error(request, "Invalid form submission.")
        
        context = {
            'profile_form': profile_form,
            'password_form': password_form,
            'user': user,
            'active_tab': active_tab
        }
        
        return render(request, self.template_name, context)
    
@method_decorator(decorators, name='dispatch')
class ExpensePDFView(View):
    """View to generate and download expense data as PDF"""
    
    template_name = 'expense_pdf.html'
    
    def get(self, request, *args, **kwargs):
        # Base queryset for all user expenses
        qs = Expense.objects.filter(owner=request.user)
        
        # Get current date and time
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)
        
        # Total expenses
        total_expense = qs.aggregate(total=Sum('amount'))['total'] or 0
        
        # Today's expenses
        today_expense = qs.filter(created_at__date=today).aggregate(total=Sum('amount'))['total'] or 0
        
        # Yesterday's expenses
        yesterday_expense = qs.filter(created_at__date=yesterday).aggregate(total=Sum('amount'))['total'] or 0
        
        # This week's expenses
        weekly_expense = qs.filter(created_at__date__gte=start_of_week).aggregate(total=Sum('amount'))['total'] or 0
        
        # This month's expenses
        monthly_expense = qs.filter(created_at__date__gte=start_of_month).aggregate(total=Sum('amount'))['total'] or 0
        
        # This year's expenses
        yearly_expense = qs.filter(created_at__date__gte=start_of_year).aggregate(total=Sum('amount'))['total'] or 0
        
        # Category-wise expenses with percentages precalculated
        category_expenses = list(qs.values('category').annotate(total=Sum('amount')).order_by('-total'))
        for item in category_expenses:
            item['percentage'] = round((item['total'] / total_expense * 100) if total_expense > 0 else 0, 1)
        
        # Payment method-wise expenses with percentages precalculated
        payment_expenses = list(qs.values('payment_method').annotate(total=Sum('amount')).order_by('-total'))
        for item in payment_expenses:
            item['percentage'] = round((item['total'] / total_expense * 100) if total_expense > 0 else 0, 1)
        
        # Monthly breakdown for the current year
        current_year = today.year
        monthly_expenses = list(
            qs.filter(created_at__year=current_year)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        
        # Format month names for better display
        for expense in monthly_expenses:
            if expense['month']:
                expense['month_name'] = expense['month'].strftime('%B')
        
        # Recent expenses for PDF detail
        recent_expenses = qs.order_by('-created_at')[:20]  # Get last 20 expenses for details
        
        context = {
            # User info
            'user': request.user,
            'generated_date': timezone.now(),
            
            # Summary totals
            'total_expense': total_expense,
            'today_expense': today_expense,
            'yesterday_expense': yesterday_expense,
            'weekly_expense': weekly_expense,
            'monthly_expense': monthly_expense,
            'yearly_expense': yearly_expense,
            
            # Detailed breakdowns with precalculated percentages
            'category_expenses': category_expenses,
            'payment_expenses': payment_expenses,
            'monthly_expenses': monthly_expenses,
            'recent_expenses': recent_expenses,
            
            # Date references
            'today': today,
            'start_of_week': start_of_week,
            'start_of_month': start_of_month,
            'start_of_year': start_of_year,
        }
        
        # Render template to HTML string
        template = get_template(self.template_name)
        html = template.render(context)
        
        # Create PDF from HTML
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        # Check if PDF generation was successful
        if not pdf.err:
            # Generate response with PDF
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f"expenses_{today.strftime('%Y%m%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        # If PDF generation failed, return error response
        return HttpResponse("Error generating PDF", status=500)

@method_decorator(decorators, name='dispatch')
class ExpensePeriodPDFView(View):
    """View to generate and download expense data for a specific period as PDF"""
    
    template_name = 'expense_pdf.html'
    
    def get(self, request, *args, **kwargs):
        # Get period parameters
        period = request.GET.get('period', 'all')  # all, month, week, year
        
        # Base queryset for all user expenses
        qs = Expense.objects.filter(owner=request.user)
        
        # Get current date and time
        today = timezone.now().date()
        start_date = None
        period_name = "All Time"
        
        # Filter based on period
        if period == 'month':
            start_date = today.replace(day=1)
            period_name = f"Month of {today.strftime('%B %Y')}"
            qs = qs.filter(created_at__date__gte=start_date)
        elif period == 'week':
            start_date = today - timedelta(days=today.weekday())
            period_name = f"Week of {start_date.strftime('%b %d')} to {today.strftime('%b %d, %Y')}"
            qs = qs.filter(created_at__date__gte=start_date)
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            period_name = f"Year {today.year}"
            qs = qs.filter(created_at__date__gte=start_date)
        
        # Total for the period
        total_expense = qs.aggregate(total=Sum('amount'))['total'] or 0
        
        # Category-wise expenses with percentages precalculated
        category_expenses = list(qs.values('category').annotate(total=Sum('amount')).order_by('-total'))
        for item in category_expenses:
            item['percentage'] = round((item['total'] / total_expense * 100) if total_expense > 0 else 0, 1)
        
        # Payment method-wise expenses with percentages precalculated
        payment_expenses = list(qs.values('payment_method').annotate(total=Sum('amount')).order_by('-total'))
        for item in payment_expenses:
            item['percentage'] = round((item['total'] / total_expense * 100) if total_expense > 0 else 0, 1)
        
        # All expenses for this period
        period_expenses = qs.order_by('-created_at')
        
        context = {
            # User info
            'user': request.user,
            'generated_date': timezone.now(),
            'period_name': period_name,
            
            # Summary total
            'total_expense': total_expense,
            
            # Detailed breakdowns with precalculated percentages
            'category_expenses': category_expenses,
            'payment_expenses': payment_expenses,
            'period_expenses': period_expenses,
            
            # For template conditional rendering
            'is_period_report': True,
        }
        
        # Render template to HTML string
        template = get_template(self.template_name)
        html = template.render(context)
        
        # Create PDF from HTML
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        # Check if PDF generation was successful
        if not pdf.err:
            # Generate response with PDF
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f"expenses_{period}_{today.strftime('%Y%m%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        # If PDF generation failed, return error response
        return HttpResponse("Error generating PDF", status=500)


# admin based views
@method_decorator(decorators, name='dispatch')
class AdminDashboardView(View):
    template_name = 'admin_dashboard.html'
    def get(self, request, *args, **kwargs):
        # Get all users
        users = User.objects.all()
        
        # Get all expenses
        expenses = Expense.objects.all()
        
        # Get total expenses
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Get total users
        total_users = users.count()
        
        # Get today's date
        today = timezone.now().date()
        
        # Get today's expenses
        today_expenses = expenses.filter(created_at__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
        
        context = {
            'users': users,
            'expenses': expenses,
            'total_expenses': total_expenses,
            'total_users': total_users,
            'today_expenses': today_expenses,
        }
        
        return render(request, self.template_name, context)

@method_decorator(decorators, name='dispatch')
class AdminUserListView(View):
    template_name = 'admin_user_list.html'
    
    def get(self, request, *args, **kwargs):
        # Get all users
        users = User.objects.all()
        
        context = {
            'users': users,
        }
        
        return render(request, self.template_name, context)

@method_decorator(decorators, name='dispatch')
class AdminUserDeleteView(View):
    
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = User.objects.get(id=user_id)
        if user.role == 'admin':
            return redirect('admin_user_list')
        
        # Delete the user
        user.delete()
        
        return redirect('admin_user_list')
    
@method_decorator(decorators, name='dispatch')
class AdminUserExpenseView(View):
    template_name = 'admin_user_expense_list.html'
    
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = User.objects.get(id=user_id)
        
        # Get all expenses for the user
        expenses = Expense.objects.filter(owner=user)
        
        context = {
            'user': user,
            'expenses': expenses,
        }
        
        return render(request, self.template_name, context)

@method_decorator(decorators, name='dispatch')    
class AdminAllUsersAnalysisView(View):
    template_name = 'admin_all_users_analysis.html'
    
    def get(self, request, *args, **kwargs):
        # Get all users (excluding superusers for more focused analysis)
        users = User.objects.all().exclude(is_superuser=True)
        
        # Prepare data for all users
        user_data = []
        total_system_expenses = 0
        today = timezone.now().date()
        
        for user in users:
            # Get all expenses for THIS specific user
            expenses = Expense.objects.filter(owner=user)
            
            # Get total expenses for the user
            total_user_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
            total_system_expenses += total_user_expenses
            
            # Get today's expenses for the user
            today_expenses = expenses.filter(created_at__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
            
            # Get last 30 days expenses
            thirty_days_ago = today - timedelta(days=30)
            monthly_expenses = expenses.filter(created_at__date__gte=thirty_days_ago).aggregate(Sum('amount'))['amount__sum'] or 0
            
            # Get expense count
            expense_count = expenses.count()
            
            # Get last activity (most recent expense)
            last_activity = expenses.order_by('-created_at').first()
            
            # Get average expense amount
            avg_expense = expenses.aggregate(Avg('amount'))['amount__avg'] or 0
            
            # Get most expensive category if categorized
            if hasattr(Expense, 'category'):
                try:
                    category_sums = expenses.values('category').annotate(sum=Sum('amount')).order_by('-sum')
                    top_category = category_sums.first() if category_sums else None
                    top_category_name = top_category['category'] if top_category else 'N/A'
                    top_category_amount = top_category['sum'] if top_category else 0
                except:
                    top_category_name = 'N/A'
                    top_category_amount = 0
            else:
                top_category_name = 'Categories not enabled'
                top_category_amount = 0
            
            # Collect user data
            user_data.append({
                'user': user,
                'total_expenses': total_user_expenses,
                'today_expenses': today_expenses,
                'monthly_expenses': monthly_expenses,
                'expense_count': expense_count,
                'last_activity': last_activity.created_at if last_activity else None,
                'avg_expense': round(avg_expense, 2),
                'top_category': top_category_name,
                'top_category_amount': top_category_amount,
            })
        
        # Sort users by total expenses (highest first)
        user_data.sort(key=lambda x: x['total_expenses'], reverse=True)
        
        # Calculate system-wide metrics
        active_users_today = sum(1 for u in user_data if u['today_expenses'] > 0)
        active_users_month = sum(1 for u in user_data if u['monthly_expenses'] > 0)
        
        # System average expense - Calculate from user-specific data to avoid double-counting
        all_expense_count = sum(u['expense_count'] for u in user_data)
        system_avg_expense = total_system_expenses / all_expense_count if all_expense_count > 0 else 0
        
        # Get total expenses by day for the last 30 days for charting
        daily_totals = []
        for i in range(30):
            day = today - timedelta(days=i)
            day_total = Expense.objects.filter(created_at__date=day).aggregate(Sum('amount'))['amount__sum'] or 0
            daily_totals.append({
                'date': day.strftime('%Y-%m-%d'),
                'total': day_total
            })
        
        context = {
            'user_data': user_data,
            'total_users': users.count(),
            'total_system_expenses': total_system_expenses,
            'active_users_today': active_users_today,
            'active_users_month': active_users_month,
            'system_avg_expense': round(system_avg_expense, 2),
            'daily_totals': daily_totals,
        }
        
        return render(request, self.template_name, context)
    

# forget password views

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from .models import User  # Import your custom user model

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generate token and uid
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Prepare email
            subject = 'Password Reset Request'
            email_template = 'reset_password_email.html'
            email_context = {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'TRAVELIX',
            }
            
            html_message = render_to_string(email_template, email_context)
            plain_message = f"Hi {user.username}, click this link to reset your password: {reset_url}"
            
            # Send email
            send_mail(
                subject,
                plain_message,
                'noreply@yourwebsite.com',
                [email],
                html_message=html_message,
                fail_silently=False
            )
            
            messages.success(request, "Password reset link has been sent to your email.")
            return redirect('signin')
            
        except User.DoesNotExist:
            messages.error(request, "No account found with that email address.")
    
    return render(request, 'forgot_password.html')

def password_reset_confirm(request, uidb64, token):
    try:
        # Decode the user id
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        # Verify token
        if not default_token_generator.check_token(user, token):
            messages.error(request, "Password reset link is invalid or has expired.")
            return redirect('forgot_password')
        
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 != password2:
                messages.error(request, "Passwords don't match.")
                return render(request, 'password_reset_confirm.html')
            
            # Set new password
            user.set_password(password1)
            user.save()
            
            messages.success(request, "Password has been reset successfully. You can now log in with your new password.")
            return redirect('signin')
            
        return render(request, 'password_reset_confirm.html')
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Password reset link is invalid.")
        return redirect('forgot_password')
   

# targets/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import MonthlyTarget, WeeklyTarget, YearlyTarget
from .forms import MonthlyTargetForm, WeeklyTargetForm, YearlyTargetForm


@login_required
def target_dashboard(request):
    """Display all targets for the current user"""
    monthly_targets = MonthlyTarget.objects.filter(user=request.user).order_by('-year', '-month')
    weekly_targets = WeeklyTarget.objects.filter(user=request.user).order_by('-week_start_date')
    yearly_targets = YearlyTarget.objects.filter(user=request.user).order_by('-year')
    
    context = {
        'monthly_targets': monthly_targets[:5],  # Show latest 5
        'weekly_targets': weekly_targets[:5],    # Show latest 5
        'yearly_targets': yearly_targets[:5],    # Show latest 5
    }
    return render(request, 'targets/dashboard.html', context)


from django.db import IntegrityError
from django.contrib import messages


@login_required
def add_monthly_target(request):
    """Add a new monthly target"""
    if request.method == 'POST':
        form = MonthlyTargetForm(request.POST)
        if form.is_valid():
            try:
                target = form.save(commit=False)
                target.user = request.user
                target.save()
                messages.success(request, 'Monthly target added successfully!')
                return redirect('target_dashboard')
            except IntegrityError:
                messages.error(request, 'A target for this month, year, and category already exists. Please edit the existing target or choose different values.')
    else:
        form = MonthlyTargetForm()
    
    return render(request, 'targets/add_monthly_target.html', {'form': form})


@login_required
def add_weekly_target(request):
    """Add a new weekly target"""
    if request.method == 'POST':
        form = WeeklyTargetForm(request.POST)
        if form.is_valid():
            try:
                target = form.save(commit=False)
                target.user = request.user
                target.save()
                messages.success(request, 'Weekly target added successfully!')
                return redirect('target_dashboard')
            except IntegrityError:
                messages.error(request, 'A target for this week and category already exists. Please edit the existing target or choose different values.')
    else:
        form = WeeklyTargetForm()
    
    return render(request, 'targets/add_weekly_target.html', {'form': form})


@login_required
def add_yearly_target(request):
    """Add a new yearly target"""
    if request.method == 'POST':
        form = YearlyTargetForm(request.POST)
        if form.is_valid():
            try:
                target = form.save(commit=False)
                target.user = request.user
                target.save()
                messages.success(request, 'Yearly target added successfully!')
                return redirect('target_dashboard')
            except IntegrityError:
                messages.error(request, 'A target for this year and category already exists. Please edit the existing target or choose different values.')
    else:
        form = YearlyTargetForm()
    
    return render(request, 'targets/add_yearly_target.html', {'form': form})


@login_required
def edit_monthly_target(request, target_id):
    """Edit an existing monthly target"""
    target = get_object_or_404(MonthlyTarget, id=target_id, user=request.user)
    
    if request.method == 'POST':
        form = MonthlyTargetForm(request.POST, instance=target)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Monthly target updated successfully!')
                return redirect('target_dashboard')
            except IntegrityError:
                messages.error(request, 'A target for this month, year, and category already exists. Please choose different values.')
    else:
        form = MonthlyTargetForm(instance=target)
    
    return render(request, 'targets/edit_monthly_target.html', {'form': form, 'target': target})


@login_required
def edit_weekly_target(request, target_id):
    """Edit an existing weekly target"""
    target = get_object_or_404(WeeklyTarget, id=target_id, user=request.user)
    
    if request.method == 'POST':
        form = WeeklyTargetForm(request.POST, instance=target)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Weekly target updated successfully!')
                return redirect('target_dashboard')
            except IntegrityError:
                messages.error(request, 'A target for this week and category already exists. Please choose different values.')
    else:
        form = WeeklyTargetForm(instance=target)
    
    return render(request, 'targets/edit_weekly_target.html', {'form': form, 'target': target})


@login_required
def edit_yearly_target(request, target_id):
    """Edit an existing yearly target"""
    target = get_object_or_404(YearlyTarget, id=target_id, user=request.user)
    
    if request.method == 'POST':
        form = YearlyTargetForm(request.POST, instance=target)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Yearly target updated successfully!')
                return redirect('target_dashboard')
            except IntegrityError:
                messages.error(request, 'A target for this year and category already exists. Please choose different values.')
    else:
        form = YearlyTargetForm(instance=target)
    
    return render(request, 'targets/edit_yearly_target.html', {'form': form, 'target': target})


@login_required
def delete_monthly_target(request, target_id):
    """Delete a monthly target"""
    target = get_object_or_404(MonthlyTarget, id=target_id, user=request.user)
    
    if request.method == 'POST':
        target.delete()
        messages.success(request, 'Monthly target deleted successfully!')
        return redirect('target_dashboard')
    
    return render(request, 'targets/confirm_delete.html', {
        'target': target,
        'target_type': 'Monthly',
        'delete_url': 'delete_monthly_target'
    })


@login_required
def delete_weekly_target(request, target_id):
    """Delete a weekly target"""
    target = get_object_or_404(WeeklyTarget, id=target_id, user=request.user)
    
    if request.method == 'POST':
        target.delete()
        messages.success(request, 'Weekly target deleted successfully!')
        return redirect('target_dashboard')
    
    return render(request, 'targets/confirm_delete.html', {
        'target': target,
        'target_type': 'Weekly',
        'delete_url': 'delete_weekly_target'
    })


@login_required
def delete_yearly_target(request, target_id):
    """Delete a yearly target"""
    target = get_object_or_404(YearlyTarget, id=target_id, user=request.user)
    
    if request.method == 'POST':
        target.delete()
        messages.success(request, 'Yearly target deleted successfully!')
        return redirect('target_dashboard')
    
    return render(request, 'targets/confirm_delete.html', {
        'target': target,
        'target_type': 'Yearly',
        'delete_url': 'delete_yearly_target'
    })


@login_required
def monthly_targets_list(request):
    """List all monthly targets with pagination"""
    targets = MonthlyTarget.objects.filter(user=request.user).order_by('-year', '-month')
    paginator = Paginator(targets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'targets/monthly_targets_list.html', {'page_obj': page_obj})


@login_required
def weekly_targets_list(request):
    """List all weekly targets with pagination"""
    targets = WeeklyTarget.objects.filter(user=request.user).order_by('-week_start_date')
    paginator = Paginator(targets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'targets/weekly_targets_list.html', {'page_obj': page_obj})


@login_required
def yearly_targets_list(request):
    """List all yearly targets with pagination"""
    targets = YearlyTarget.objects.filter(user=request.user).order_by('-year')
    paginator = Paginator(targets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'targets/yearly_targets_list.html', {'page_obj': page_obj})