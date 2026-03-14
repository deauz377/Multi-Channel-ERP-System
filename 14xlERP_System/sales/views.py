from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from datetime import datetime, timedelta
from .models import Invoice, InvoiceItem, Payment
from .forms import InvoiceForm, InvoiceItemForm, PaymentForm

def sales_overview(request):
    # Get today's sales
    today = datetime.now().date()
    sales_today = Invoice.objects.filter(date=today).aggregate(total=Sum('total'))['total'] or 0

    # Get this month's sales
    month_start = today.replace(day=1)
    sales_month = Invoice.objects.filter(date__gte=month_start).aggregate(total=Sum('total'))['total'] or 0

    # Get total outstanding payments
    outstanding = Invoice.objects.aggregate(total=Sum('total'), paid=Sum('paid'))['total'] or 0
    total_paid = Invoice.objects.aggregate(paid=Sum('paid'))['paid'] or 0
    outstanding_amount = outstanding - total_paid

    # Get recent invoices
    recent_invoices = Invoice.objects.all().order_by('-date')[:5]

    # Get top selling products (by quantity)
    top_products = InvoiceItem.objects.values('product__name').annotate(
        total_quantity=Sum('qty')
    ).order_by('-total_quantity')[:5]

    context = {
        'sales_today': sales_today,
        'sales_month': sales_month,
        'outstanding_amount': outstanding_amount,
        'recent_invoices': recent_invoices,
        'top_products': top_products,
    }
    return render(request, 'sales/overview.html', context)

def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-date')
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        invoices = invoices.filter(
            Q(id__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )

    if status_filter:
        if status_filter == 'paid':
            invoices = invoices.filter(paid__gte=models.F('total'))
        elif status_filter == 'partial':
            invoices = invoices.filter(paid__gt=0, paid__lt=models.F('total'))
        elif status_filter == 'unpaid':
            invoices = invoices.filter(paid=0)

    context = {
        'invoices': invoices,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'sales/invoice_list.html', context)

def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, 'Invoice created! Add items below.')
            return redirect('sales:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
    return render(request, 'sales/invoice_form.html', {'form': form, 'title': 'Create Invoice'})

def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.items.all()
    return render(request, 'sales/invoice_detail.html', {'invoice': invoice, 'items': items})

def invoice_item_add(request, invoice_pk):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    if request.method == 'POST':
        form = InvoiceItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.invoice = invoice
            item.save()
            messages.success(request, 'Item added to invoice!')
            return redirect('sales:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceItemForm()
    return render(request, 'sales/invoice_item_form.html', {'form': form, 'invoice': invoice})

def payment_record(request, invoice_pk):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.save()
            invoice.paid += payment.amount
            invoice.save()
            messages.success(request, 'Payment recorded!')
            return redirect('sales:invoice_detail', pk=invoice.pk)
    else:
        form = PaymentForm()
    return render(request, 'sales/payment_form.html', {'form': form, 'invoice': invoice})

