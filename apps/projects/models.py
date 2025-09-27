import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Project(models.Model):
    class AppType(models.TextChoices):
        ANDROID = 'ANDROID', _('Android')
        IOS = 'IOS', _('iOS')
        BOTH = 'BOTH', _('Both')

    class DeploymentOption(models.TextChoices):
        NOT_CHOSEN = 'NOT_CHOSEN', _('Not Chosen')
        AMAZON_S3 = 'AMAZON_S3', _('Amazon S3')
        GOOGLE_PLAY = 'GOOGLE_PLAY', _('Google Play Store')
        APP_STORE = 'APP_STORE', _('Apple App Store')

    class ProjectStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        ANALYSIS_PENDING = 'ANALYSIS_PENDING', _('Analysis Pending')
        ANALYSIS_COMPLETE = 'ANALYSIS_COMPLETE', _('Analysis Complete')
        DESIGN_PENDING = 'DESIGN_PENDING', _('Design Pending')
        DESIGN_COMPLETE = 'DESIGN_COMPLETE', _('Design Complete')
        CODE_GENERATION = 'CODE_GENERATION', _('Code Generation')
        QA_PENDING = 'QA_PENDING', _('QA Pending')
        QA_COMPLETE = 'QA_COMPLETE', _('QA Complete')
        DEPLOYMENT_PENDING = 'DEPLOYMENT_PENDING', _('Deployment Pending')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    source_url = models.URLField(max_length=1024, blank=True, null=True)
    app_type = models.CharField(max_length=10, choices=AppType.choices, default=AppType.ANDROID)
    status = models.CharField(max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.PENDING)
    status_message = models.CharField(max_length=255, blank=True, null=True)
    user_persona_document = models.TextField(blank=True, null=True)
    brand_palette = models.JSONField(blank=True, null=True)
    generated_code_path = models.CharField(max_length=1024, blank=True, null=True)
    deployment_option = models.CharField(max_length=20, choices=DeploymentOption.choices, default=DeploymentOption.NOT_CHOSEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('owner', 'name')

    def __str__(self):
        return self.name