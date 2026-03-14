from django.db import models

# Create your models here.

class Expense(models.Model):
    business = models.ForeignKey('core.Business', on_delete=models.CASCADE, null=True, blank=True)
    CATEGORY_CHOICES = [
        ('rent','Rent'),
        ('salaries','Salaries'),
        ('transport','Transport'),
        ('utilities','Utilities'),
        ('other','Other'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.category} - {self.amount}"
