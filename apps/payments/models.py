import uuid
from django.db import models
from django.conf import settings
from apps.projects.models import Project

class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESSFUL = 'SUCCESSFUL', 'Successful'
        FAILED = 'FAILED', 'Failed'

    class PlanType(models.TextChoices):
        ONETIME = 'ONETIME', 'One-Time'
        MONTHLY = 'MONTHLY', 'Monthly'
        YEARLY = 'YEARLY', 'Yearly'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField()
    paystack_reference = models.CharField(max_length=100, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    plan_type = models.CharField(max_length=20, choices=PlanType.choices, default=PlanType.ONETIME)
    
    # New fields for subscription management
    subscription_code = models.CharField(max_length=100, blank=True, null=True, help_text="Paystack subscription code for recurring billing.")
    plan_code = models.CharField(max_length=100, blank=True, null=True, help_text="Paystack plan code associated with this subscription.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment of {self.amount} for {self.project.name} ({self.plan_type} - {self.status})"
