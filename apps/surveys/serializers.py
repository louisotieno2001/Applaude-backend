from rest_framework import serializers
from .models import SurveyResponse, AppRating, UserFeedback

class SurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = '__all__'

class AppRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppRating
        fields = '__all__'

class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = '__all__'
