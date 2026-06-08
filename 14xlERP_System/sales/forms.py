from django import forms
from .models import Invoice, InvoiceItem, Payment, Order, OrderItem

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 'discount']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Discount amount'}),
        }

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'qty', 'price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'qty': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_type', 'customer', 'supplier', 'status']
        widgets = {
            'order_type': forms.Select(attrs={'class': 'form-select'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        order_type = cleaned_data.get('order_type')
        customer = cleaned_data.get('customer')
        supplier = cleaned_data.get('supplier')

        if order_type == 'customer' and not customer:
            raise forms.ValidationError('Customer is required for customer orders.')
        if order_type == 'supplier' and not supplier:
            raise forms.ValidationError('Supplier is required for supplier orders.')
        return cleaned_data

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'qty', 'price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'qty': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['method', 'amount']
        widgets = {
            'method': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
