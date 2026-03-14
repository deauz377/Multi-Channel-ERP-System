from django.shortcuts import render
from django.db.models import Sum, F
from django.utils import timezone

from sales.models import Invoice
from inventory.models import Product
from expenses.models import Expense
from customers.models import Customer


# Create your views here.

def overview(request):
    today = timezone.now().date()
    sales_today = Invoice.objects.filter(date__date=today).aggregate(Sum('total'))['total__sum'] or 0
    stock_value = Product.objects.aggregate(
        value=Sum(F('quantity') * F('retail_price'))
    )['value'] or 0
    expenses_month = Expense.objects.filter(date__month=today.month).aggregate(Sum('amount'))['amount__sum'] or 0
    profit = sales_today - expenses_month
    debtors = Customer.objects.filter(balance__gt=0)
    creditors = []
    context = {
        'sales_today': sales_today,
        'stock_value': stock_value,
        'expenses_month': expenses_month,
        'profit': profit,
        'debtors': debtors,
        'creditors': creditors,
    }
    return render(request, 'dashboard/overview.html', context)

