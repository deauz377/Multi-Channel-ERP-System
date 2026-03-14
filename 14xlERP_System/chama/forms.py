from django import forms
from .models import Contribution, Loan

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['member', 'amount', 'date', 'business']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter amount'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'business': forms.Select(attrs={'class': 'form-select'}),
        }

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['member', 'principal', 'interest', 'due_date', 'business']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-select'}),
            'principal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Loan amount'}),
            'interest': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Interest rate (%)'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'business': forms.Select(attrs={'class': 'form-select'}),
        }