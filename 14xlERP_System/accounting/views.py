from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from .models import (
    ChartOfAccounts, Journal, JournalEntry, Invoice, InvoiceItem,
    Bill, BillItem, BankAccount, BankTransaction, Budget, BudgetLine,
    FinancialReport, TaxConfiguration, MPesaIntegration, BankReconciliation
)
from .forms import (
    ChartOfAccountsForm, JournalForm, JournalEntryForm, InvoiceForm,
    BillForm, BankAccountForm, BankTransactionForm, BudgetForm,
    TaxConfigurationForm, MPesaIntegrationForm, BankReconciliationForm
)


@login_required
def accounting_dashboard(request):
    """Accounting dashboard overview"""
    tenant = request.user.profile.tenant if hasattr(request.user, 'profile') else None
    
    # Calculate totals
    total_receivables = Invoice.objects.filter(tenant=tenant, status__in=['partial', 'issued']).aggregate(
        total=Sum('balance_due'))['total'] or 0
    total_payables = Bill.objects.filter(tenant=tenant, status__in=['partial', 'received']).aggregate(
        total=Sum('balance_due'))['total'] or 0
    
    context = {
        'chart_accounts': ChartOfAccounts.objects.filter(tenant=tenant).count() if tenant else 0,
        'invoices': Invoice.objects.filter(tenant=tenant, status__in=['issued', 'sent']).count() if tenant else 0,
        'bills': Bill.objects.filter(tenant=tenant, status__in=['received', 'partial']).count() if tenant else 0,
        'total_receivables': total_receivables,
        'total_payables': total_payables,
        'bank_accounts': BankAccount.objects.filter(tenant=tenant).count() if tenant else 0,
        'recent_invoices': Invoice.objects.filter(tenant=tenant)[:5] if tenant else [],
        'recent_bills': Bill.objects.filter(tenant=tenant)[:5] if tenant else [],
    }
    return render(request, 'accounting/dashboard.html', context)


class ChartOfAccountsListView(LoginRequiredMixin, ListView):
    model = ChartOfAccounts
    template_name = 'accounting/chart_of_accounts_list.html'
    context_object_name = 'accounts'
    paginate_by = 20

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return ChartOfAccounts.objects.filter(tenant=tenant).order_by('account_number')
        return ChartOfAccounts.objects.none()


class ChartOfAccountsCreateView(LoginRequiredMixin, CreateView):
    model = ChartOfAccounts
    form_class = ChartOfAccountsForm
    template_name = 'accounting/chart_of_accounts_form.html'
    success_url = reverse_lazy('accounting:chart_accounts_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        messages.success(self.request, 'Chart of accounts created successfully!')
        return super().form_valid(form)


class JournalListView(LoginRequiredMixin, ListView):
    model = Journal
    template_name = 'accounting/journal_list.html'
    context_object_name = 'journals'
    paginate_by = 10

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return Journal.objects.filter(tenant=tenant)
        return Journal.objects.none()


class JournalCreateView(LoginRequiredMixin, CreateView):
    model = Journal
    form_class = JournalForm
    template_name = 'accounting/journal_form.html'
    success_url = reverse_lazy('accounting:journal_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        messages.success(self.request, 'Journal created successfully!')
        return super().form_valid(form)


class JournalEntryListView(LoginRequiredMixin, ListView):
    model = JournalEntry
    template_name = 'accounting/journal_entry_list.html'
    context_object_name = 'entries'
    paginate_by = 20

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return JournalEntry.objects.filter(tenant=tenant).order_by('-entry_date')
        return JournalEntry.objects.none()


class JournalEntryCreateView(LoginRequiredMixin, CreateView):
    model = JournalEntry
    form_class = JournalEntryForm
    template_name = 'accounting/journal_entry_form.html'
    success_url = reverse_lazy('accounting:entry_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Journal entry created successfully!')
        return super().form_valid(form)


@login_required
def post_journal_entry(request, pk):
    """Post a journal entry to GL"""
    entry = get_object_or_404(JournalEntry, pk=pk)
    if request.method == 'POST':
        entry.is_posted = True
        entry.posted_date = datetime.now()
        entry.save()
        messages.success(request, 'Journal entry posted successfully!')
        return redirect('accounting:entry_list')
    return render(request, 'accounting/post_journal_entry.html', {'entry': entry})


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'accounting/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return Invoice.objects.filter(tenant=tenant).order_by('-invoice_date')
        return Invoice.objects.none()


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'accounting/invoice_detail.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        return context


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'accounting/invoice_form.html'
    success_url = reverse_lazy('accounting:invoice_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Invoice created successfully!')
        return super().form_valid(form)


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'accounting/invoice_form.html'
    success_url = reverse_lazy('accounting:invoice_list')

    def form_valid(self, form):
        messages.success(self.request, 'Invoice updated successfully!')
        return super().form_valid(form)


@login_required
def mark_invoice_paid(request, pk):
    """Mark invoice as paid"""
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.status = 'paid'
        invoice.paid_amount = invoice.total_amount
        invoice.save()
        messages.success(request, 'Invoice marked as paid!')
        return redirect('accounting:invoice_detail', pk=pk)
    return render(request, 'accounting/mark_invoice_paid.html', {'invoice': invoice})


class BillListView(LoginRequiredMixin, ListView):
    model = Bill
    template_name = 'accounting/bill_list.html'
    context_object_name = 'bills'
    paginate_by = 20

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return Bill.objects.filter(tenant=tenant).order_by('-bill_date')
        return Bill.objects.none()


class BillDetailView(LoginRequiredMixin, DetailView):
    model = Bill
    template_name = 'accounting/bill_detail.html'
    context_object_name = 'bill'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        return context


class BillCreateView(LoginRequiredMixin, CreateView):
    model = Bill
    form_class = BillForm
    template_name = 'accounting/bill_form.html'
    success_url = reverse_lazy('accounting:bill_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        messages.success(self.request, 'Bill created successfully!')
        return super().form_valid(form)


class BankAccountListView(LoginRequiredMixin, ListView):
    model = BankAccount
    template_name = 'accounting/bank_account_list.html'
    context_object_name = 'accounts'
    paginate_by = 10

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return BankAccount.objects.filter(tenant=tenant)
        return BankAccount.objects.none()


class BankAccountCreateView(LoginRequiredMixin, CreateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = 'accounting/bank_account_form.html'
    success_url = reverse_lazy('accounting:bank_account_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        messages.success(self.request, 'Bank account created successfully!')
        return super().form_valid(form)


class BankTransactionListView(LoginRequiredMixin, ListView):
    model = BankTransaction
    template_name = 'accounting/bank_transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return BankTransaction.objects.filter(tenant=tenant).order_by('-transaction_date')
        return BankTransaction.objects.none()


class BankTransactionCreateView(LoginRequiredMixin, CreateView):
    model = BankTransaction
    form_class = BankTransactionForm
    template_name = 'accounting/bank_transaction_form.html'
    success_url = reverse_lazy('accounting:bank_transaction_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        messages.success(self.request, 'Bank transaction created successfully!')
        return super().form_valid(form)


class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'accounting/budget_list.html'
    context_object_name = 'budgets'
    paginate_by = 10

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return Budget.objects.filter(tenant=tenant).order_by('-fiscal_year')
        return Budget.objects.none()


class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'accounting/budget_form.html'
    success_url = reverse_lazy('accounting:budget_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        messages.success(self.request, 'Budget created successfully!')
        return super().form_valid(form)


@login_required
def trial_balance_report(request):
    """Generate trial balance report"""
    tenant = request.user.profile.tenant if hasattr(request.user, 'profile') else None
    accounts = ChartOfAccounts.objects.filter(tenant=tenant) if tenant else []
    
    context = {
        'accounts': accounts,
        'total_debits': sum(acc.get_balance() for acc in accounts if acc.account_type in ['asset', 'expense']),
        'total_credits': sum(acc.get_balance() for acc in accounts if acc.account_type in ['liability', 'equity', 'revenue']),
    }
    return render(request, 'accounting/trial_balance.html', context)


@login_required
def bank_reconciliation(request):
    """Bank reconciliation view"""
    tenant = request.user.profile.tenant if hasattr(request.user, 'profile') else None
    accounts = BankAccount.objects.filter(tenant=tenant) if tenant else []
    
    if request.method == 'POST':
        reconciliation = BankReconciliation.objects.create(
            tenant=tenant,
            bank_account_id=request.POST.get('bank_account'),
            reconciliation_date=datetime.strptime(request.POST.get('reconciliation_date'), '%Y-%m-%d').date(),
            bank_balance=request.POST.get('bank_balance'),
            book_balance=request.POST.get('book_balance'),
            reconciled_by=request.user
        )
        messages.success(request, 'Bank reconciliation completed!')
        return redirect('accounting:dashboard')
    
    return render(request, 'accounting/bank_reconciliation.html', {'accounts': accounts})
