from .base_agent_anthropic import BaseAgent
from .prompts.super_prompts import DEVOPS_AGENT_PERSONA, DEVOPS_AGENT_GOAL
from apps.projects.models import Project
from django.db import transaction

class DeploymentAgent(BaseAgent):
    """
    Simulates the deployment of the mobile application.
    """
    def __init__(self):
        super().__init__(
            agent_name="CI/CD & DevOps Specialist",
            agent_persona=DEVOPS_AGENT_PERSONA,
            goal=DEVOPS_AGENT_GOAL
        )

    def execute(self, project_id: int):
        """
        Executes the deployment simulation for the project.

        Args:
            project_id (int): The ID of the project to deploy.
        """
        print(f"Executing Deployment Agent for project {project_id}...")
        try:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                # Ensure the QA check was completed before deploying
                if project.status != Project.ProjectStatus.QA_COMPLETE:
                    raise Exception("Cannot deploy: QA check is not yet complete.")

                project.status = Project.ProjectStatus.DEPLOYMENT_PENDING
                project.status_message = "Preparing for deployment to production environment..."
                project.save()

        except Project.DoesNotExist:
            print(f"Error: Project with ID {project_id} not found.")
            return

        # Construct the task for the Vertex AI API
        task_description = f"""
        **MISSION: Simulate the CI/CD and Deployment Pipeline for a Mobile App.**

        **Input Data:**
        - **Project Name:** {project.name}
        - **App Type:** {project.app_type}
        - **Source Input:** {project.source_url}

        **Reasoning Framework (Strict Adherence Required):**
        1.  **Simulate Build Artifact Creation:** Describe creating the build artifact (e.g., an `.apk` for Android or `.ipa` for iOS).
        2.  **Simulate Containerization (for testing):** Briefly explain how you would containerize the application to ensure a consistent testing environment.
        3.  **Simulate Deployment to Staging:** Detail the process of deploying the artifact to a staging environment and running a final suite of automated tests.
        4.  **Simulate Promotion to Production:** Describe the final step of promoting the build to the production environment, making it live.
        5.  **Generate Confirmation:** Output a final success message and, most importantly, a simulated but realistic-looking download URL for the deployed application. The URL should follow the format: `https://cdn.applaude.ai/apps/{project.id}/app.apk` (for Android) or `https://apps.apple.com/yourapp/{project.name.lower().replace(' ', '')}` (for iOS).

        **Output Constraint:**
        You MUST return a single, clean, valid Markdown-formatted report detailing these simulated steps and concluding with the final deployment link.
        """

        full_prompt = self._generate_prompt(task_description)

        try:
            # Use Anthropic API call through BaseAgent's model
            deployment_report = self.generate_content(full_prompt)

            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.COMPLETED
                project.status_message = "Deployment successful. Your app is live!"
                project.deployment_platform = "Applaude" # Mark where it's 'hosted'
                project.generated_code_path = f"https://cdn.applaude.ai/apps/{project.id}/app.apk"
                project.save()

            self.send_status_notification(project)

            print(f"Deployment simulation complete for project {project_id}. Project is marked as COMPLETED.")
            return deployment_report

        except Exception as e:
            # Handle potential race conditions or other DB errors
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.FAILED
                project.status_message = f"Deployment failed: {e}"
                project.save()
            print(f"Error during final deployment update for project {project_id}: {e}")
            raise
