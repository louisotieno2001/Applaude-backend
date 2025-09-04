from rest_framework import serializers
from apps.projects.models import Project

class ApiClientCreateSerializer(serializers.Serializer):
    """
    Serializer for validating the creation of a new API Client.
    It's used for input validation only and does not map directly to a model.
    """
    business_name = serializers.CharField(max_length=255)
    website_link = serializers.URLField(max_length=500)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class APIProjectCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a project via the API.
    """
    class Meta:
        model = Project
        fields = ['source_url', 'app_type']
