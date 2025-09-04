from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from apps.projects.models import Project

@shared_task
def send_project_reminder_emails():
    """
    Sends reminder emails to users with unfinished projects.
    """
    yesterday = timezone.now() - timedelta(days=1)
    three_days_ago = timezone.now() - timedelta(days=3)
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    # Reminder after 24 hours
    projects_24h = Project.objects.filter(
        last_completed_step=Project.LastCompletedStep.CREATED,
        updated_at__lt=yesterday
    )
    for project in projects_24h:
        send_mail(
            'Complete your Applause project',
            f'Hi {project.owner.username},\n\nYour project "{project.name}" is waiting for you. Complete the payment to start the build process!',
            'noreply@applause.ai',
            [project.owner.email],
            fail_silently=False,
        )

    # Add similar logic for 3-day and 7-day reminders
