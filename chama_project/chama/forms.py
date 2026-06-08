from django import forms
from .models import Member, Contribution, Loan, LoanPayment


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
        }


class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['member', 'amount', 'date', 'description']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Enter amount',
                'min': '0'
            }),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add notes (optional)',
                'rows': 3
            }),
        }


class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['member', 'principal', 'interest', 'due_date', 'description']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-select'}),
            'principal': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Loan amount',
                'min': '0'
            }),
            'interest': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Interest rate (%)',
                'min': '0'
            }),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Loan purpose or notes (optional)',
                'rows': 3
            }),
        }


class LoanPaymentForm(forms.ModelForm):
    class Meta:
        model = LoanPayment
        fields = ['amount', 'payment_date', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Payment amount',
                'min': '0'
            }),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Payment notes (optional)',
                'rows': 3
            }),
        }
