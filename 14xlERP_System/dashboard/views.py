from django.shortcuts import render
from django.db.models import Sum, F, Count
from django.utils import timezone
from datetime import timedelta
import json

from sales.models import Invoice
from inventory.models import Product
from expenses.models import Expense
from customers.models import Customer


def overview(request):
    today = timezone.now().date()
    current_month = today.replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)

    # KPI Calculations
    sales_today = Invoice.objects.filter(date__date=today).aggregate(Sum('total'))['total__sum'] or 0
    sales_month = Invoice.objects.filter(
        date__date__gte=current_month
    ).aggregate(Sum('total'))['total__sum'] or 0
    sales_last_month = Invoice.objects.filter(
        date__date__gte=last_month,
        date__date__lt=current_month
    ).aggregate(Sum('total'))['total__sum'] or 0

    stock_value = Product.objects.aggregate(
        value=Sum(F('quantity') * F('retail_price'))
    )['value'] or 0
    total_products = Product.objects.count()
    low_stock_count = Product.objects.filter(quantity__lte=F('minimum_stock')).count()

    expenses_today = Expense.objects.filter(date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    expenses_month = Expense.objects.filter(
        date__gte=current_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    profit_today = sales_today - expenses_today
    profit_month = sales_month - expenses_month

    # Sales by category/product for bar chart
    top_products = Product.objects.order_by('-quantity')[:5].values('name', 'quantity', 'retail_price')

    # Recent transactions
    recent_invoices = Invoice.objects.all().order_by('-date')[:8].select_related('customer').values(
        'id', 'customer__name', 'total', 'paid', 'date'
    )

    recent_expenses = Expense.objects.all().order_by('-date')[:5].values(
        'id', 'description', 'amount', 'category', 'date'
    )

    # Chart data: Sales trend (last 7 days)
    sales_trend = []
    labels = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        sales = Invoice.objects.filter(date__date=date).aggregate(Sum('total'))['total__sum'] or 0
        sales_trend.append(float(sales))
        labels.append(date.strftime('%a'))

    # Chart data: Expenses by category
    expense_categories = Expense.objects.filter(
        date__gte=current_month
    ).values('category').annotate(total=Sum('amount')).order_by('-total')[:6]

    expense_labels = [e['category'] for e in expense_categories]
    expense_data = [float(e['total']) for e in expense_categories]

    # Chart data: Top products
    top_products_list = Product.objects.order_by('-quantity')[:5].values('name', 'quantity', 'retail_price')
    product_labels = [p['name'][:15] for p in top_products_list]
    product_data = [p['quantity'] for p in top_products_list]

    debtors = Customer.objects.filter(balance__gt=0).order_by('-balance')[:5]

    # Prepare context
    context = {
        'sales_today': sales_today,
        'sales_month': sales_month,
        'sales_last_month': sales_last_month,
        'stock_value': stock_value,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'expenses_today': expenses_today,
        'expenses_month': expenses_month,
        'profit_today': profit_today,
        'profit_month': profit_month,
        'recent_invoices': recent_invoices,
        'recent_expenses': recent_expenses,
        'top_products': top_products,
        'debtors': debtors,

        # Chart data as JSON
        'sales_trend_data': json.dumps(sales_trend),
        'sales_trend_labels': json.dumps(labels),
        'expense_labels': json.dumps(expense_labels),
        'expense_data': json.dumps(expense_data),
        'product_labels': json.dumps(product_labels),
        'product_data': json.dumps(product_data),
    }
    return render(request, 'dashboard/overview.html', context)

