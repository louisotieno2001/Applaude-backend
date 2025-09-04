from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Tenant(TenantMixin):
    """
    Represents a tenant in the multi-tenant architecture.
    Each tenant has its own isolated database schema.
    """
    name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)

    # This field is required by django-tenants
    auto_create_schema = True

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    """
    Represents a domain that maps to a specific tenant.
    For example, 'user-a.applause.com' would map to User A's tenant.
    """
    def __str__(self):
        return self.domain
