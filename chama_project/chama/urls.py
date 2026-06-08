from django.urls import path
from . import views

app_name = 'chama'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Members
    path('members/', views.member_list, name='member_list'),
    path('members/create/', views.member_create, name='member_create'),
    path('members/<int:pk>/', views.member_detail, name='member_detail'),
    
    # Contributions
    path('contributions/', views.contribution_list, name='contribution_list'),
    path('contributions/add/', views.contribution_create, name='contribution_create'),
    path('contributions/<int:pk>/', views.contribution_detail, name='contribution_detail'),
    
    # Loans
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/add/', views.loan_create, name='loan_create'),
    path('loans/<int:pk>/', views.loan_detail, name='loan_detail'),
    path('loans/<int:pk>/approve/', views.loan_approve, name='loan_approve'),
    path('loans/<int:pk>/activate/', views.loan_activate, name='loan_activate'),
    path('loans/<int:loan_pk>/payment/add/', views.loan_payment_add, name='loan_payment_add'),
]
