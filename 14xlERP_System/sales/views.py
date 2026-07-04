from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from datetime import datetime, timedelta
from .models import Invoice, InvoiceItem, Payment, Order, OrderItem
from .forms import InvoiceForm, InvoiceItemForm, PaymentForm, OrderForm, OrderItemForm

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
            invoices = invoices.filter(paid__gte=F('total'))
        elif status_filter == 'partial':
            invoices = invoices.filter(paid__gt=0, paid__lt=F('total'))
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
    item_rows = []
    for item in items:
        item_rows.append({
            'product_name': item.product.name,
            'qty': item.qty,
            'price': item.price,
            'subtotal': item.qty * item.price,
        })
    return render(request, 'sales/invoice_detail.html', {'invoice': invoice, 'items': item_rows})


def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, 'Invoice deleted successfully.')
        return redirect('sales:invoice_list')
    return render(request, 'sales/invoice_confirm_delete.html', {'invoice': invoice})


def order_list(request):
    orders = Order.objects.all().order_by('-date')
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )

    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'sales/order_list.html', context)


def order_create(request):
    initial = {}
    if request.GET.get('order_type'):
        initial['order_type'] = request.GET.get('order_type')
    if request.GET.get('supplier'):
        initial['supplier'] = request.GET.get('supplier')
    if request.GET.get('customer'):
        initial['customer'] = request.GET.get('customer')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if order.order_type == 'customer':
                order.supplier = None
            else:
                order.customer = None
            order.total = 0
            order.save()
            messages.success(request, 'Order created! Add items below.')
            return redirect('sales:order_detail', pk=order.pk)
    else:
        form = OrderForm(initial=initial)
    return render(request, 'sales/order_form.html', {'form': form, 'title': 'Create Order'})


def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.all()
    return render(request, 'sales/order_detail.html', {'order': order, 'items': items})


def order_item_add(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    if request.method == 'POST':
        form = OrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.order = order
            item.save()
            total = order.items.aggregate(total=Sum(F('price') * F('qty')))['total'] or 0
            order.total = total
            order.save()
            messages.success(request, 'Item added to order!')
            return redirect('sales:order_detail', pk=order.pk)
    else:
        form = OrderItemForm()
    return render(request, 'sales/order_item_form.html', {'form': form, 'order': order})


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

