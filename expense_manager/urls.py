"""
URL configuration for expense_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from expense import views

urlpatterns = [
 
    path('', views.HomeView.as_view(), name='home'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('signin/', views.SignInView.as_view(), name='signin'),
    path('signout/', views.SignOutView.as_view(), name='signout'),
    path('index/', views.indexView.as_view(), name='index'),
    path('expense/remove/<int:pk>', views.ExpenceDeleteView.as_view(), name='expense-delete'),
    path('expense/change/<int:pk>', views.ExpenseUpdateView.as_view(), name='expense-update'),
    path('expense/summary', views.ExpenseSummaryView.as_view(), name='expense-summary'),
    path('api/', include('api.urls')),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('expense/pdf/', views.ExpensePDFView.as_view(), name='expense_pdf'),
    path('expense/pdf/period/', views.ExpensePeriodPDFView.as_view(), name='expense_period_pdf'),

    #ADMIN URLS
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/user/list/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/user/<int:pk>/delete/', views.AdminUserDeleteView.as_view(), name='admin_user_delete'),
    path('admin/user/expense/<int:pk>/', views.AdminUserExpenseView.as_view(), name='admin_user_expense'),
    path('admin/users/analysis/', views.AdminAllUsersAnalysisView.as_view(), name='admin_all_users_analysis'),
       
    # forget password

    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),


#targets URLs

   path('targets/', views.target_dashboard, name='target_dashboard'),
    
    # Add targets
    path('targets/add/monthly/', views.add_monthly_target, name='add_monthly_target'),
    path('targets/add/weekly/', views.add_weekly_target, name='add_weekly_target'),
    path('targets/add/yearly/', views.add_yearly_target, name='add_yearly_target'),
    
    # Edit targets
    path('targets/edit/monthly/<int:target_id>/', views.edit_monthly_target, name='edit_monthly_target'),
    path('targets/edit/weekly/<int:target_id>/', views.edit_weekly_target, name='edit_weekly_target'),
    path('targets/edit/yearly/<int:target_id>/', views.edit_yearly_target, name='edit_yearly_target'),
    
    # Delete targets
    path('targets/delete/monthly/<int:target_id>/', views.delete_monthly_target, name='delete_monthly_target'),
    path('targets/delete/weekly/<int:target_id>/', views.delete_weekly_target, name='delete_weekly_target'),
    path('targets/delete/yearly/<int:target_id>/', views.delete_yearly_target, name='delete_yearly_target'),
    
    # List all targets
    path('targets/monthly/', views.monthly_targets_list, name='monthly_targets_list'),
    path('targets/weekly/', views.weekly_targets_list, name='weekly_targets_list'),
    path('targets/yearly/', views.yearly_targets_list, name='yearly_targets_list'),
 


]

