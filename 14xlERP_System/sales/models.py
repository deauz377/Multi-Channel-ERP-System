from django.db import models
from tenants.models import TenantModel
from inventory.models import Product

# Create your models here.

class Invoice(TenantModel):
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.name}"

class Order(TenantModel):
    ORDER_TYPE_CHOICES = [
        ('customer', 'Customer Order'),
        ('supplier', 'Supplier Order'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
    ]

    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='customer')
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, null=True, blank=True)
    supplier = models.ForeignKey('inventory.Supplier', on_delete=models.PROTECT, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        if self.order_type == 'supplier' and self.supplier:
            return f"Purchase Order #{self.id} - {self.supplier.name}"
        return f"Order #{self.id} - {self.customer.name if self.customer else 'Unknown'}"

    @property
    def partner_name(self):
        return self.supplier.name if self.order_type == 'supplier' and self.supplier else self.customer.name if self.customer else 'Unknown'

class InvoiceItem(TenantModel):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.qty} x {self.product.name}"

class OrderItem(TenantModel):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.qty} x {self.product.name}"

    @property
    def line_total(self):
        return self.qty * self.price

class Payment(TenantModel):
    METHOD_CHOICES = [
        ('cash','Cash'),
        ('mpesa','M-Pesa'),
        ('bank','Bank'),
    ]
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} payment of {self.amount}"

