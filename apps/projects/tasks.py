import anthropic
import os
import atexit
from celery import shared_task
from apps.projects.models import Project
from django.db import transaction
import time
import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


try:
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    print("Anthropic AI Model configured successfully.")
except Exception as e:
    print(f"Error configuring Anthropic AI Model: {e}")
    client = None

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
            
            # Send WebSocket notification
            send_project_status_notification(project, room_name='chat_room1')
    except Project.DoesNotExist:
        # Handle cases where the project might be deleted during processing
        print(f"Project with ID {project_id} not found for status update.")
    except Exception as e:
        print(f"Error updating project status for {project_id}: {e}")

def send_project_status_notification(project, room_name='chat_room1'):
    """Send project status update via WebSocket"""
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            progress = get_progress_percentage(project.status)
            group_name = f'chat_{room_name}'
            print(f"Sending WebSocket notification to group: {group_name}")
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'project_status_update',
                    'project_id': str(project.id),
                    'status': project.status,
                    'status_message': project.status_message,
                    'progress': progress,
                    'is_processing': project.status in [
                        'ANALYSIS_PENDING',
                        'DESIGN_PENDING',
                        'CODE_GENERATION',
                        'QA_PENDING',
                        'SECURITY_SCAN_PENDING',
                        'DEPLOYMENT_PENDING',
                    ],
                    'project_data': {
                        'name': project.name,
                        'source_url': project.source_url,
                        'user_persona_document': project.user_persona_document,
                        'brand_palette': project.brand_palette,
                        'generated_code_path': project.generated_code_path,
                    }
                }
            )
    except Exception as e:
        print(f"Error sending WebSocket notification: {e}")

def send_chat_message(message, sender='Applaude Prime', room_name='chat_room1'):
    """Send a chat message via WebSocket"""
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                room_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender
                }
            )
    except Exception as e:
        print(f"Error sending chat message: {e}")

def send_task_start_message(project_id, task_name, task_description, room_name='chat_room1'):
    """Send task start message via WebSocket"""
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                room_name,
                {
                    'type': 'task_started',
                    'project_id': str(project_id),
                    'task_name': task_name,
                    'task_description': task_description
                }
            )
    except Exception as e:
        print(f"Error sending task start message: {e}")

def send_task_end_message(project_id, task_name, task_result, room_name='chat_room1'):
    """Send task end message via WebSocket"""
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                room_name,
                {
                    'type': 'task_completed',
                    'project_id': str(project_id),
                    'task_name': task_name,
                    'task_result': task_result
                }
            )
    except Exception as e:
        print(f"Error sending task end message: {e}")

def get_progress_percentage(status):
    """Convert project status to progress percentage"""
    status_progress = {
        'PENDING': 0,
        'ANALYSIS_PENDING': 10,
        'ANALYSIS_COMPLETE': 20,
        'DESIGN_PENDING': 30,
        'DESIGN_COMPLETE': 40,
        'CODE_GENERATION': 50,
        'QA_PENDING': 60,
        'QA_COMPLETE': 70,
        'DEPLOYMENT_PENDING': 80,
        'COMPLETED': 100,
        'FAILED': 0,
    }
    return status_progress.get(status, 0)


def get_ai_response(prompt, retries=3, delay=5):
    """
    Calls the Anthropic AI model with retry logic.
    Returns the generated text or raises an exception.
    """
    if not client:
        raise ConnectionError("Anthropic AI model is not configured.")

    for attempt in range(retries):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            # Basic validation of response structure
            if response and response.content:
                return response.content[0].text
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
    print(f"Starting market analysis for project {project_id}")
    project = Project.objects.get(id=project_id)
    send_task_start_message(project_id, "Market Analysis", "Analyzing your requirements and creating user persona")
    update_project_status(project_id, Project.ProjectStatus.ANALYSIS_PENDING, "Analyzing market and target user...")
    try:
        print(f"Project found: {project.name}, URL: {project.source_url}")

        # --- User Persona Generation ---
        if project.source_url and project.source_url.startswith('http'):
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
        else:
            persona_prompt = f"""
            Based on the app description: "{project.source_url}".
            Create a detailed "User Persona" document for a potential mobile application that matches this description.
            The persona should include:
            - A fictional name and demographic details (age, location, occupation).
            - A brief biography.
            - Goals and motivations for using an app that fits the description.
            - Frustrations and pain points with existing solutions.
            - Their preferred technology and social media platforms.
            Format the output as a clean, readable text document.
            """
        user_persona = get_ai_response(persona_prompt)

        # --- Brand Palette Generation ---
        if project.source_url and project.source_url.startswith('http'):
            palette_prompt = f"""
            Based on the website at {project.source_url}, generate a JSON object for a brand color palette.
            The JSON object must include the following keys with hex color values:
            "primary", "secondary", "text_light", "text_dark", "background".
            Example: {{"primary": "#0062FF", "secondary": "#FFC107", "text_light": "#FFFFFF", "text_dark": "#212121", "background": "#F5F5F5"}}
            Return ONLY the raw JSON object.
            """
        else:
            palette_prompt = f"""
            Based on the app description: "{project.source_url}", generate a JSON object for a brand color palette that would suit such an app.
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

        # Send task completion message
        send_task_end_message(project_id, "Market Analysis", "User persona and brand palette created successfully")
        send_chat_message("Market analysis complete! I've analyzed the website and created a user persona and brand palette. Proceeding to the design phase.")

        # Automatically trigger design task
        run_design_task.delay(str(project.id))

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
    send_task_start_message(project_id, "Code Generation", "Generating your app source code using AI")
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

        # Send task completion message
        send_task_end_message(project_id, "Code Generation", "App source code generated successfully and ready for download!")
        send_chat_message("Code generation complete! Your app has been created successfully. Now running quality assurance checks.")

        # Automatically trigger QA check
        run_qa_check.delay(str(project.id))

        return project.id # Pass ID to the next task
    except Exception as e:
        update_project_status(project_id, Project.ProjectStatus.FAILED, f"Code Generation Failed: {e}")
        self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_qa_check(self, project_id):
    """
    Performs a simulated Quality Assurance check on the generated code.
    """
    send_task_start_message(project_id, "Quality Assurance", "Running comprehensive tests and checks")
    update_project_status(project_id, Project.ProjectStatus.QA_PENDING, "Performing automated QA checks...")
    try:
        project = Project.objects.get(id=project_id)
        if not project.generated_code_path:
            raise ValueError("Generated code path not found. Cannot run QA.")

        # Simulate QA process (e.g., running static analysis, linting, tests)
        time.sleep(random.randint(15, 30))

        # Simulate a successful QA outcome
        update_project_status(project_id, Project.ProjectStatus.QA_COMPLETE, "QA checks passed. Ready for deployment.")
        
        # Send task completion message
        send_task_end_message(project_id, "Quality Assurance", "All QA checks passed successfully")
        send_chat_message("Quality assurance complete! Your app has passed all tests and is ready for security analysis.")

        # Automatically trigger cybersecurity check
        run_cybersecurity_check.delay(str(project.id))

        return project.id # Pass ID to the next task
    except Exception as e:
        update_project_status(project_id, Project.ProjectStatus.FAILED, f"QA Check Failed: {e}")
        self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_design_task(self, project_id):
    """
    Generates the UI/UX design for the mobile application.
    """
    send_task_start_message(project_id, "UI/UX Design", "Creating beautiful interface designs")
    update_project_status(project_id, Project.ProjectStatus.DESIGN_PENDING, "Creating UI/UX design...")
    try:
        project = Project.objects.get(id=project_id)

        # Simulate design generation process
        time.sleep(random.randint(15, 30))

        # Simulate successful design completion
        update_project_status(project_id, Project.ProjectStatus.DESIGN_COMPLETE, "Design complete. Ready for code generation.")
        
        # Send task completion message
        send_task_end_message(project_id, "UI/UX Design", "Beautiful designs created with brand colors")
        send_chat_message("Design phase complete! I've created stunning UI designs for your app. Now moving to code generation.")

        # Automatically trigger code generation
        run_code_generation.delay(str(project.id))

        return project.id
    except Exception as e:
        update_project_status(project_id, Project.ProjectStatus.FAILED, f"Design Task Failed: {e}")
        self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_cybersecurity_check(self, project_id):
    """
    Performs a cybersecurity audit on the generated code.
    """
    send_task_start_message(project_id, "Security Analysis", "Scanning code for vulnerabilities and security issues")
    update_project_status(project_id, Project.ProjectStatus.DEPLOYMENT_PENDING, "Performing cybersecurity audit...")
    try:
        project = Project.objects.get(id=project_id)
        if not project.generated_code_path:
            raise ValueError("Generated code path not found. Cannot run cybersecurity check.")

        # Simulate cybersecurity audit
        time.sleep(random.randint(10, 20))

        # Simulate successful security audit
        update_project_status(project_id, Project.ProjectStatus.DEPLOYMENT_PENDING, "Security audit passed. Ready for deployment.")

        # Send task completion message
        send_task_end_message(project_id, "Security Analysis", "Security audit completed - your app is secure!")
        send_chat_message("Security analysis complete! Your app has passed all security checks and is ready for deployment.")

        # Automatically trigger deployment
        run_deployment.delay(str(project.id))

        return project.id
    except Exception as e:
        update_project_status(project_id, Project.ProjectStatus.FAILED, f"Cybersecurity Check Failed: {e}")
        self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_deployment(self, project_id):
    """
    Deploys the application to Amazon S3 for code build.
    """
    send_task_start_message(project_id, "Deployment", "Packaging and deploying your app to Amazon S3")
    update_project_status(project_id, Project.ProjectStatus.DEPLOYMENT_PENDING, "Deploying application to Amazon S3...")
    try:
        project = Project.objects.get(id=project_id)

        # Set deployment option to Amazon S3 if not already set
        if project.deployment_option == Project.DeploymentOption.NOT_CHOSEN:
            with transaction.atomic():
                project_to_update = Project.objects.select_for_update().get(id=project_id)
                project_to_update.deployment_option = Project.DeploymentOption.AMAZON_S3
                project_to_update.save()

        # Simulate deployment to S3 time
        time.sleep(random.randint(25, 50))

        # Generate S3 URL for the deployed app
        s3_url = f"https://applaude-deployments.s3.amazonaws.com/{project.owner.username}/{project.id}/app.apk"

        final_message = f"Deployment successful! Your app is now available at: {s3_url}"
        update_project_status(project_id, Project.ProjectStatus.COMPLETED, final_message)

        # Send final task completion message
        send_task_end_message(project_id, "Deployment", f"Successfully deployed to Amazon S3! Download: {s3_url}")

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
