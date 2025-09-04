import google.generativeai as genai
import os
from celery import shared_task, atexit
from apps.projects.models import Project
from django.db import transaction
import time
import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail


try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    print("AI Model configured successfully.")
except Exception as e:
    print(f"Error configuring AI Model: {e}")
    model = None

# --- Helper Functions ---

def update_project_status(project_id, status, message=None):
    """Atomically updates the project status and an optional message."""
    try:
        with transaction.atomic():
            project = Project.objects.select_for_update().get(id=project_id)
            project.status = status
            if message:
                project.status_message = message
            project.save()
    except Project.DoesNotExist:
        # Handle cases where the project might be deleted during processing
        print(f"Project with ID {project_id} not found for status update.")
    except Exception as e:
        print(f"Error updating project status for {project_id}: {e}")


def get_ai_response(prompt, retries=3, delay=5):
    """
    Calls the generative AI model with retry logic.
    Returns the generated text or raises an exception.
    """
    if not model:
        raise ConnectionError("Generative AI model is not configured.")

    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            # Basic validation of response structure
            if response and response.text:
                return response.text
            else:
                raise ValueError("Received an empty or invalid response from the AI model.")
        except Exception as e:
            print(f"AI generation attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise  # Re-raise the final exception

# --- Core AI Agent Tasks ---

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_market_analysis(self, project_id):
    """
    Analyzes the provided source URL to generate a user persona and brand identity.
    """
    update_project_status(project_id, Project.ProjectStatus.ANALYSIS_PENDING, "Analyzing market and target user...")
    try:
        project = Project.objects.get(id=project_id)

        # --- User Persona Generation ---
        persona_prompt = f"""
        Analyze the content from the URL: {project.source_url}.
        Based on this analysis, create a detailed "User Persona" document for a potential mobile application.
        The persona should include:
        - A fictional name and demographic details (age, location, occupation).
        - A brief biography.
        - Goals and motivations for using an app related to the source content.
        - Frustrations and pain points with existing solutions.
        - Their preferred technology and social media platforms.
        Format the output as a clean, readable text document.
        """
        user_persona = get_ai_response(persona_prompt)

        # --- Brand Palette Generation ---
        palette_prompt = f"""
        Based on the website at {project.source_url}, generate a JSON object for a brand color palette.
        The JSON object must include the following keys with hex color values:
        "primary", "secondary", "text_light", "text_dark", "background".
        Example: {{"primary": "#0062FF", "secondary": "#FFC107", "text_light": "#FFFFFF", "text_dark": "#212121", "background": "#F5F5F5"}}
        Return ONLY the raw JSON object.
        """
        brand_palette_str = get_ai_response(palette_prompt)

        # Atomically update the project with the generated assets
        with transaction.atomic():
            project_to_update = Project.objects.select_for_update().get(id=project_id)
            project_to_update.user_persona_document = user_persona
            project_to_update.brand_palette = brand_palette_str # Storing as string, serializer will handle JSON
            project_to_update.status = Project.ProjectStatus.ANALYSIS_COMPLETE
            project_to_update.status_message = "Market analysis complete. Ready for design."
            project_to_update.save()

        return project.id # Pass the project ID to the next task in the chain
    except Exception as e:
        update_project_status(project_id, Project.ProjectStatus.FAILED, f"Market Analysis Failed: {e}")
        self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_code_generation(self, project_id):
    """
    Generates the application code based on the project requirements.
    This is a placeholder for a complex code generation process.
    """
    update_project_status(project_id, Project.ProjectStatus.CODE_GENERATION, "Generating application source code...")
    try:
        project = Project.objects.get(id=project_id)

        # In a real system, this would involve a complex series of prompts
        # and interactions with a code-specialized AI model.
        # Here, we simulate the process and success.

        # Simulate generation time
        time.sleep(random.randint(20, 40))

        # Simulate storing the generated code and getting a path
        # This path would point to an S3 bucket or similar storage.
        generated_code_path = f"s3://applause-code-bucket/{project.owner.username}/{project.id}/source_code.zip"

        with transaction.atomic():
            project_to_update = Project.objects.select_for_update().get(id=project_id)
            project_to_update.generated_code_path = generated_code_path
            project_to_update.status_message = "Code generation finished. Pending QA."
            project_to_update.save()

        return project.id # Pass ID to the next task
    except Exception as e:
        update_project_status(project_id, Project.ProjectStatus.FAILED, f"Code Generation Failed: {e}")
        self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_qa_check(self, project_id):
    """
    Performs a simulated Quality Assurance check on the generated code.
    """
    update_project_status(project_id, Project.ProjectStatus.QA_PENDING, "Performing automated QA checks...")
    try:
        project = Project.objects.get(id=project_id)
        if not project.generated_code_path:
            raise ValueError("Generated code path not found. Cannot run QA.")

        # Simulate QA process (e.g., running static analysis, linting, tests)
        time.sleep(random.randint(15, 30))

        # Simulate a successful QA outcome
        update_project_status(project_id, Project.ProjectStatus.QA_COMPLETE, "QA checks passed. Ready for deployment.")

        return project.id # Pass ID to the next task
    except Exception as e:
        update_project_status(project_id, Project.ProjectStatus.FAILED, f"QA Check Failed: {e}")
        self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_deployment(self, project_id):
    """
    Simulates the deployment of the application to the chosen platform.
    """
    update_project_status(project_id, Project.ProjectStatus.DEPLOYMENT_PENDING, "Deploying application...")
    try:
        project = Project.objects.get(id=project_id)
        if project.deployment_option == Project.DeploymentOption.NOT_CHOSEN:
            # If no deployment option was chosen, complete the process here.
            final_message = "Project build complete. Download the code or choose a deployment option."
            update_project_status(project_id, Project.ProjectStatus.COMPLETED, final_message)
            return project.id

        # Simulate deployment time
        time.sleep(random.randint(25, 50))

        final_message = f"Deployment successful! Your app is now live on the {project.deployment_option} platform."
        update_project_status(project_id, Project.ProjectStatus.COMPLETED, final_message)

        return project.id
    except Exception as e:
        update_project_status(project_id, Project.ProjectStatus.FAILED, f"Deployment Failed: {e}")
        self.retry(exc=e)

@shared_task(name="send_testimonial_requests")
def send_testimonial_requests():
    """
    A periodic Celery task that identifies users who are good candidates
    for providing a testimonial and sends them a request.
    """
    now = timezone.now()
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")


    # Define time windows for sending requests
    one_day_ago = now - timedelta(days=1)
    one_month_ago = now - timedelta(days=30)
    three_months_ago = now - timedelta(days=90)

    # Find projects that were completed recently
    # We check for a small window to avoid sending emails every day for the same project
    completed_recently = Project.objects.filter(
        status=Project.ProjectStatus.COMPLETED,
        updated_at__range=(one_day_ago - timedelta(hours=24), one_day_ago)
    )

    completed_one_month_ago = Project.objects.filter(
        status=Project.ProjectStatus.COMPLETED,
        updated_at__range=(one_month_ago - timedelta(hours=24), one_month_ago)
    )

    completed_three_months_ago = Project.objects.filter(
        status=Project.ProjectStatus.COMPLETED,
        updated_at__range=(three_months_ago - timedelta(hours=24), three_months_ago)
    )

    projects_to_notify = list(completed_recently) + list(completed_one_month_ago) + list(completed_three_months_ago)

    for project in projects_to_notify:
        user = project.owner
        # You would ideally check if a testimonial already exists for this project/user
        # from apps.testimonials.models import Testimonial
        # if not Testimonial.objects.filter(user=user, project=project).exists():

        # For this implementation, we'll assume sending the email is sufficient.

        subject = f"Share Your Experience with {project.name}"
        message = f"""
        Hi {user.username},

        We hope you're enjoying your app, "{project.name}"!

        Your feedback is incredibly valuable to us and to the Applause community. Would you be willing to share a short testimonial about your experience building with us?

        It will only take a moment, and you can submit it directly here:
        {frontend_url}/submit-testimonial/{project.id}

        Thank you for being a part of the Applause journey!

        Best,
        The Applause Team
        """

        try:
            send_mail(
                subject,
                message,
                'noreply@applaude.ai',
                [user.email],
                fail_silently=False,
            )
            print(f"Sent testimonial request to {user.email} for project {project.name}")
        except Exception as e:
            print(f"Failed to send testimonial request email to {user.email}: {e}")


# --- Cleanup ---

@atexit.register
def cleanup_resources(*args, **kwargs):
    """
    A cleanup function to be executed when the Celery worker shuts down.
    """
    print("Celery worker is shutting down. Performing cleanup...")
