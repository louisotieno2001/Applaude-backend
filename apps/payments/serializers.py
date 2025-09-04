from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'project', 'amount', 'status', 
            'paystack_reference', 'plan_type', 'subscription_code', 
            'plan_code', 'created_at'
        ]
        read_only_fields = ('user', 'project', 'status', 'paystack_reference', 'created_at')
