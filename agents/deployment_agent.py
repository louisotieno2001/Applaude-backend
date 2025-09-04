from .base_agent import BaseAgent
from .prompts.super_prompts import DEVOPS_AGENT_PERSONA, DEVOPS_AGENT_GOAL
from apps.projects.models import Project
from django.db import transaction
import google.generativeai as genai

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
        self.model = genai.GenerativeModel('gemini-1.5-pro')

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

        # Construct the task for the Gemini API
        task_description = f"""
        **MISSION: Simulate the CI/CD and Deployment Pipeline for a Mobile App.**

        **Input Data:**
        - **Project Name:** {project.name}
        - **App Type:** {project.app_type}

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
        # In a real application, you would make the API call:
        # response = self.model.generate_content(full_prompt)
        # deployment_report = response.text

        # For this simulation, we will create a representative report.
        deployment_report = f"""
        ### CI/CD Pipeline Simulation Report for {project.name}

        **1. Build Artifact Creation:**
        - Successfully compiled the {project.app_type} source code.
        - Generated build artifact: `app-release.apk`.

        **2. Containerization for Testing:**
        - Packaged the build artifact and its dependencies into a Docker container for isolated, consistent automated testing.

        **3. Deployment to Staging & Automated Testing:**
        - Deployed the container to the Staging environment.
        - Executed a full suite of automated UI and integration tests. All tests passed.

        **4. Promotion to Production:**
        - Promoted the verified build to the production servers.
        - The new version is now live and propagating through the CDN.

        **Deployment Complete:**
        Your application is now available at the following URL:
        [https://cdn.applaude.ai/apps/{project.id}/app.apk](https://cdn.applaude.ai/apps/{project.id}/app.apk)
        """

        try:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.COMPLETED
                project.status_message = "Deployment successful. Your app is live!"
                project.deployment_platform = "Applaude" # Mark where it's 'hosted'
                project.generated_code_path = f"https://cdn.applaude.ai/apps/{project.id}/app.apk"
                project.save()

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
