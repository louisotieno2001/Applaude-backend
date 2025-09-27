from rest_framework import serializers
from .models import Project
from .utils import highlight_code
from apps.users.serializers import UserDetailSerializer
from apps.testimonials.models import Testimonial

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.
    Optimizes database lookups.
    """
    owner = UserDetailSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Project
        fields = (
            'id',
            'owner',
            'name',
            'source_url',
            'app_type',
            'status',
            'status_display',
            'status_message',
            'user_persona_document',
            'brand_palette',
            'generated_code_path',
            'deployment_option',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'owner', 'status', 'status_display', 'status_message', 'created_at', 'updated_at')

    def create(self, validated_data):
        """
        Create a new project instance.
        The owner is already set in validated_data by the view's perform_create.
        """
        project = Project.objects.create(**validated_data)
        return project
