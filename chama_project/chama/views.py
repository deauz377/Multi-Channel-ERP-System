from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.views.decorators.http import require_http_methods
from .models import Member, Contribution, Loan, LoanPayment
from .forms import ContributionForm, LoanForm, MemberForm


@login_required
def dashboard(request):
    """Chama dashboard showing key statistics"""
    try:
        member = request.user.chama_member
    except Member.DoesNotExist:
        messages.warning(request, 'Please create a member profile first.')
        return redirect('chama:member_create')
    
    # Get statistics
    total_contributions = Contribution.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_loans = Loan.objects.aggregate(total=Sum('principal'))['total'] or 0
    active_loans = Loan.objects.filter(status__in=['active', 'pending']).count()
    total_members = Member.objects.filter(is_active=True).count()
    
    # Recent contributions
    recent_contributions = Contribution.objects.select_related('member').order_by('-date')[:10]
    
    # Active loans
    active_loans_list = Loan.objects.select_related('member').filter(
        status__in=['active', 'pending']
    ).order_by('due_date')[:10]
    
    # Member contributions summary
    top_contributors = Contribution.objects.values('member__name').annotate(
        total_contributed=Sum('amount')
    ).order_by('-total_contributed')[:5]
    
    context = {
        'total_contributions': total_contributions,
        'total_loans': total_loans,
        'active_loans': active_loans,
        'total_members': total_members,
        'recent_contributions': recent_contributions,
        'active_loans_list': active_loans_list,
        'top_contributors': top_contributors,
    }
    return render(request, 'chama/dashboard.html', context)


@login_required
def member_create(request):
    """Create a member profile"""
    if hasattr(request.user, 'chama_member'):
        return redirect('chama:dashboard')
    
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.user = request.user
            member.save()
            messages.success(request, 'Member profile created successfully!')
            return redirect('chama:dashboard')
    else:
        form = MemberForm()
    
    return render(request, 'chama/member_form.html', {'form': form, 'title': 'Create Member Profile'})


@login_required
def contribution_list(request):
    """List all contributions"""
    contributions = Contribution.objects.select_related('member').order_by('-date')
    return render(request, 'chama/contribution_list.html', {'contributions': contributions})


@login_required
def contribution_create(request):
    """Record a new contribution"""
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contribution recorded successfully!')
            return redirect('chama:contribution_list')
    else:
        form = ContributionForm()
    
    return render(request, 'chama/contribution_form.html', {'form': form, 'title': 'Record Contribution'})


@login_required
def contribution_detail(request, pk):
    """View contribution details"""
    contribution = get_object_or_404(Contribution, pk=pk)
    return render(request, 'chama/contribution_detail.html', {'contribution': contribution})


@login_required
def loan_list(request):
    """List all loans"""
    status = request.GET.get('status')
    loans = Loan.objects.select_related('member')
    
    if status:
        loans = loans.filter(status=status)
    
    loans = loans.order_by('-created_at')
    return render(request, 'chama/loan_list.html', {'loans': loans, 'current_status': status})


@login_required
def loan_create(request):
    """Create a new loan"""
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan created successfully!')
            return redirect('chama:loan_list')
    else:
        form = LoanForm()
    
    return render(request, 'chama/loan_form.html', {'form': form, 'title': 'Create Loan'})


@login_required
def loan_detail(request, pk):
    """View loan details"""
    loan = get_object_or_404(Loan, pk=pk)
    payments = loan.payments.all()
    
    context = {
        'loan': loan,
        'payments': payments,
        'total_paid': sum(p.amount for p in payments),
    }
    return render(request, 'chama/loan_detail.html', context)


@login_required
@require_http_methods(["POST"])
def loan_approve(request, pk):
    """Approve a pending loan"""
    loan = get_object_or_404(Loan, pk=pk)
    if loan.status == 'pending':
        loan.status = 'approved'
        loan.save()
        messages.success(request, 'Loan approved successfully!')
    return redirect('chama:loan_detail', pk=pk)


@login_required
@require_http_methods(["POST"])
def loan_activate(request, pk):
    """Activate an approved loan (disburse)"""
    loan = get_object_or_404(Loan, pk=pk)
    if loan.status == 'approved':
        loan.status = 'active'
        loan.save()
        messages.success(request, 'Loan activated and disbursed!')
    return redirect('chama:loan_detail', pk=pk)


@login_required
def loan_payment_add(request, loan_pk):
    """Record a loan payment"""
    loan = get_object_or_404(Loan, pk=loan_pk)
    
    if request.method == 'POST':
        try:
            amount = request.POST.get('amount')
            payment_date = request.POST.get('payment_date')
            notes = request.POST.get('notes', '')
            
            payment = LoanPayment.objects.create(
                loan=loan,
                amount=amount,
                payment_date=payment_date,
                notes=notes
            )
            
            # Check if loan is fully paid
            total_paid = sum(p.amount for p in loan.payments.all())
            if total_paid >= loan.total_amount:
                loan.status = 'paid'
                loan.save()
                messages.success(request, 'Payment recorded! Loan marked as paid.')
            else:
                messages.success(request, 'Payment recorded successfully!')
            
            return redirect('chama:loan_detail', pk=loan_pk)
        except Exception as e:
            messages.error(request, f'Error recording payment: {str(e)}')
    
    context = {'loan': loan}
    return render(request, 'chama/loan_payment_form.html', context)


@login_required
def member_list(request):
    """List all members"""
    members = Member.objects.filter(is_active=True).prefetch_related('contributions', 'loans')
    return render(request, 'chama/member_list.html', {'members': members})


@login_required
def member_detail(request, pk):
    """View member details and statistics"""
    member = get_object_or_404(Member, pk=pk)
    total_contributed = member.contributions.aggregate(total=Sum('amount'))['total'] or 0
    total_loans = member.loans.aggregate(total=Sum('principal'))['total'] or 0
    
    context = {
        'member': member,
        'total_contributed': total_contributed,
        'total_loans': total_loans,
        'contributions': member.contributions.all(),
        'loans': member.loans.all(),
    }
    return render(request, 'chama/member_detail.html', context)
