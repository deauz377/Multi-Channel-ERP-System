from django.db import models
from tenants.models import TenantModel

# Create your models here.

class Contribution(TenantModel):
    member = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.member.name} - {self.amount}"

class Loan(TenantModel):
    member = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)
    principal = models.DecimalField(max_digits=12, decimal_places=2)
    interest = models.DecimalField(max_digits=6, decimal_places=2)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Loan {self.id} - {self.member.name}"
