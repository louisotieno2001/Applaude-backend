import uuid
import secrets
from django.db import models
from django.conf import settings

def generate_api_key():
    """
    Generates a secure, random API key.
    """
    return secrets.token_hex(32)

class APIKey(models.Model):
    """
    Represents a unique API key for a user to access Applaude services programmatically.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='api_keys')
    key = models.CharField(max_length=40, unique=True, editable=False)
    name = models.CharField(max_length=100, help_text="A descriptive name for the API key, e.g., 'My Production Server'.")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    def generate_key(self):
        return uuid.uuid4().hex

    def __str__(self):
        return f"API Key for {self.user.email} | Name: {self.name}"

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        ordering = ['-created_at']

