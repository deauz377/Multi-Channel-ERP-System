from django.urls import path
from . import views

app_name = 'chama'

urlpatterns = [
    path('', views.chama_overview, name='chama_overview'),
    path('contributions/', views.contribution_list, name='contribution_list'),
    path('contributions/add/', views.contribution_create, name='contribution_create'),
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/add/', views.loan_create, name='loan_create'),
    path('loans/<int:pk>/mark-paid/', views.loan_mark_paid, name='loan_mark_paid'),
    # Backward compatibility
    path('list/', views.chama_list, name='chama_list'),
]
