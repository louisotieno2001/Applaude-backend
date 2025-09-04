import uuid
from django.db import models
from django.conf import settings
from apps.projects.models import Project

class Testimonial(models.Model):
    """
    Represents a user testimonial for a completed project.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='testimonials')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='testimonials')
    content = models.TextField()
    is_published = models.BooleanField(default=False, help_text="Controls whether the testimonial is publicly visible.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.user.username} for {self.project.name}"

    class Meta:
        ordering = ['-created_at']
