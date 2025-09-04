from django.contrib import admin
from .models import APIKey

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'name')
    readonly_fields = ('key', 'created_at')
    fieldsets = (
        ('API Key Information', {'fields': ('user', 'name', 'key', 'is_active')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )