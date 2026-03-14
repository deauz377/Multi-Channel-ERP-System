from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sales_overview, name='sales_overview'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/add/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_pk>/item/add/', views.invoice_item_add, name='invoice_item_add'),
    path('invoices/<int:invoice_pk>/payment/add/', views.payment_record, name='payment_record'),
]
