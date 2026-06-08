from django.db import models
from django.contrib.auth.models import User

class Member(models.Model):
    """Member model for chama (savings group)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chama_member')
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    join_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-join_date']


class Contribution(models.Model):
    """Contribution model - tracks member contributions to the group"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.name} - {self.amount}"

    class Meta:
        ordering = ['-date']


class Loan(models.Model):
    """Loan model - tracks loans given to members"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('paid', 'Paid'),
        ('defaulted', 'Defaulted'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='loans')
    principal = models.DecimalField(max_digits=12, decimal_places=2)
    interest = models.DecimalField(max_digits=6, decimal_places=2)  # Interest rate in %
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loan {self.id} - {self.member.name}"

    @property
    def is_paid(self):
        return self.status == 'paid'

    @property
    def total_amount(self):
        """Calculate total amount including interest"""
        interest_amount = self.principal * (self.interest / 100)
        return self.principal + interest_amount

    class Meta:
        ordering = ['-created_at']


class LoanPayment(models.Model):
    """Track loan payment history"""
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.loan} - {self.amount}"

    class Meta:
        ordering = ['-payment_date']
