from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from .models import Contribution, Loan
from .forms import ContributionForm, LoanForm

def chama_overview(request):
    # Get chama statistics
    total_contributions = Contribution.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_loans = Loan.objects.aggregate(total=Sum('principal'))['total'] or 0
    active_loans = Loan.objects.filter(paid=False).count()
    total_members = Contribution.objects.values('member').distinct().count()

    # Get recent contributions
    recent_contributions = Contribution.objects.all().order_by('-date')[:5]

    # Get active loans
    active_loans_list = Loan.objects.filter(paid=False).order_by('due_date')[:5]

    # Get member summary
    member_summary = Contribution.objects.values('member__name').annotate(
        total_contributed=Sum('amount'),
        loans_count=Count('member__loan', distinct=True)
    ).order_by('-total_contributed')[:5]

    context = {
        'total_contributions': total_contributions,
        'total_loans': total_loans,
        'active_loans': active_loans,
        'total_members': total_members,
        'recent_contributions': recent_contributions,
        'active_loans_list': active_loans_list,
        'member_summary': member_summary,
    }
    return render(request, 'chama/overview.html', context)

def contribution_list(request):
    contributions = Contribution.objects.all().order_by('-date')
    return render(request, 'chama/contribution_list.html', {'contributions': contributions})

def contribution_create(request):
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contribution recorded successfully!')
            return redirect('chama:contribution_list')
    else:
        form = ContributionForm()
    return render(request, 'chama/contribution_form.html', {'form': form, 'title': 'Record Contribution'})

def loan_list(request):
    loans = Loan.objects.all().order_by('-due_date')
    return render(request, 'chama/loan_list.html', {'loans': loans})

def loan_create(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan recorded successfully!')
            return redirect('chama:loan_list')
    else:
        form = LoanForm()
    return render(request, 'chama/loan_form.html', {'form': form, 'title': 'Record Loan'})

def loan_mark_paid(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    loan.paid = True
    loan.save()
    messages.success(request, f'Loan for {loan.member.name} marked as paid!')
    return redirect('chama:loan_list')

# Keep the old function for backward compatibility
def chama_list(request):
    return redirect('chama:chama_overview')

