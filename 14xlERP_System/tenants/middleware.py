import threading
from django.utils.deprecation import MiddlewareMixin

_local = threading.local()


def get_current_tenant():
    return getattr(_local, 'tenant', None)


def is_super_admin():
    return getattr(_local, 'is_super_admin', False)


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        from .models import Tenant  # Import here to avoid circular import
        # Get tenant from subdomain or session
        host = request.get_host().split(':')[0]  # Remove port
        subdomain = host.split('.')[0] if '.' in host else None

        if subdomain and subdomain != '127' and subdomain != 'localhost':
            try:
                tenant = Tenant.objects.get(subdomain=subdomain)
                _local.tenant = tenant
                _local.is_super_admin = False
                request.tenant = tenant
            except Tenant.DoesNotExist:
                # Handle invalid tenant
                _local.tenant = None
                _local.is_super_admin = False
                request.tenant = None
        else:
            # Default to 'default' tenant for localhost or no subdomain
            try:
                tenant = Tenant.objects.get(subdomain='default')
                _local.tenant = tenant
                _local.is_super_admin = False
                request.tenant = tenant
            except Tenant.DoesNotExist:
                _local.tenant = None
                _local.is_super_admin = False
                request.tenant = None

        # For super admin, allow access to all
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_super_admin:
            _local.is_super_admin = True