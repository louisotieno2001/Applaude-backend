from rest_framework import serializers
from .models import Testimonial
from apps.users.serializers import UserSerializer

class TestimonialSerializer(serializers.ModelSerializer):
    """
    Serializer for the Testimonial model.
    Includes nested user data for frontend display.
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = Testimonial
        fields = ['id', 'user', 'project', 'content', 'is_published', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
