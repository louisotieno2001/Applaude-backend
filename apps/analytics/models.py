from django.db import models
from apps.projects.models import Project

class AppAnalytics(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    active_users = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
    retention_rate = models.FloatField(default=0.0)
    # Add other metrics as needed

    class Meta:
        unique_together = ('project', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"Analytics for {self.project.name} on {self.date}"
