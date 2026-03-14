from django.db import models

# Create your models here.

class Business(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    # Additional fields like logo, tax ID, etc.

    def __str__(self):
        return self.name

