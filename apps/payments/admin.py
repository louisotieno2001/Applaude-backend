from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'user', 'amount', 'plan_type', 'status', 'created_at')
    list_filter = ('status', 'plan_type', 'created_at')
    search_fields = ('project__name', 'user__username', 'email', 'paystack_reference')
    readonly_fields = ('id', 'user', 'project', 'amount', 'email', 'paystack_reference', 'plan_type', 'created_at', 'updated_at')
    fieldsets = (
        ('Transaction Details', {'fields': ('id', 'paystack_reference', 'status', 'plan_type', 'amount')}),
        ('Subscription Info', {'fields': ('subscription_code', 'plan_code')}),
        ('Associated Entities', {'fields': ('project', 'user', 'email')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
