from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class TenantManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        from .middleware import get_current_tenant, is_super_admin  # Import here
        tenant = get_current_tenant()
        if tenant and not is_super_admin() and not hasattr(self, '_ignore_tenant'):
            return queryset.filter(tenant=tenant)
        return queryset

    def for_tenant(self, tenant):
        self._tenant = tenant
        return self

    def ignore_tenant(self):
        self._ignore_tenant = True
        return self


class Tenant(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subdomain = models.CharField(max_length=100, unique=True)  # For subdomain routing
    paid_until = models.DateTimeField()
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    is_super_admin = models.BooleanField(default=False)
    encrypted_ssn = models.CharField(max_length=11, blank=True, null=True)  # Placeholder for encryption

    class Meta:
        permissions = [
            ('view_tenant_data', 'Can view tenant data'),
            ('edit_tenant_data', 'Can edit tenant data'),
            ('delete_tenant_data', 'Can delete tenant data'),
        ]

    def clean(self):
        if self.is_super_admin and not self.is_staff:
            raise ValidationError("Super admin must be staff.")
        super().clean()


# Base model for tenant-specific models
class TenantModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True, related_name='+')

    objects = TenantManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if hasattr(self, 'tenant') and not self.tenant:
            # Set tenant from request if not set
            from django.utils.deprecation import MiddlewareMixin
            # But better to set in views
            pass
        super().save(*args, **kwargs)
