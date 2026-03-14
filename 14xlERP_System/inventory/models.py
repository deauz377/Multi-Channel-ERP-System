from django.db import models

# Create your models here.

class Supplier(models.Model):
    business = models.ForeignKey('core.Business', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    contact = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    business = models.ForeignKey('core.Business', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True)
    
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
    online_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    quantity = models.IntegerField(default=0)
    minimum_stock = models.IntegerField(default=5)
    
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL,
                                 blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name