from rest_framework import serializers
from .models import BlogPost
from apps.users.serializers import UserSerializer

class BlogPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'main_image_url', 'author', 'is_published', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
