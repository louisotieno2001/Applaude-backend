from rest_framework import serializers
from .models import AppAnalytics

class AppAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppAnalytics
        fields = '__all__'
