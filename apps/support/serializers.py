from rest_framework import serializers
from .models import Ticket, FAQ

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('id', 'user', 'subject', 'description', 'status', 'created_at')
        read_only_fields = ('user', 'status', 'created_at')

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ('id', 'question', 'answer')
