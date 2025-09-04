from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'app_type', 'created_at')
    list_filter = ('status', 'app_type', 'created_at')
    search_fields = ('name', 'owner__username', 'source_url')
    readonly_fields = ('created_at', 'updated_at', 'user_persona_document', 'brand_palette')
    fieldsets = (
        (None, {'fields': ('name', 'owner', 'source_url', 'app_type')}),
        ('Status', {'fields': ('status', 'status_message')}),
        ('Features & Deployment', {'fields': ('enable_ux_survey', 'enable_pmf_survey', 'deployment_option')}),
        ('AI Generated Assets', {'fields': ('user_persona_document', 'brand_palette')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
