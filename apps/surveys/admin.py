from django.contrib import admin
from .models import SurveyResponse, AppRating, UserFeedback

@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('project', 'survey_type', 'user_identifier', 'created_at')
    list_filter = ('survey_type', 'created_at', 'project')
    search_fields = ('project__name', 'user_identifier')
    readonly_fields = ('project', 'user_identifier', 'survey_type', 'responses', 'created_at')

@admin.register(AppRating)
class AppRatingAdmin(admin.ModelAdmin):
    list_display = ('project', 'rating', 'user_identifier', 'created_at')
    list_filter = ('rating', 'created_at', 'project')
    search_fields = ('project__name', 'user_identifier', 'comment')
    readonly_fields = ('project', 'user_identifier', 'rating', 'comment', 'created_at')

@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('project', 'user_identifier', 'created_at')
    list_filter = ('created_at', 'project')
    search_fields = ('project__name', 'user_identifier', 'feedback_text')
    readonly_fields = ('project', 'user_identifier', 'feedback_text', 'created_at')
