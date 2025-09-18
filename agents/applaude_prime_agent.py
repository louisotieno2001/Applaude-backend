from .base_agent import BaseAgent
from .tasks import (
    run_market_analysis,
    run_design_task,
    run_code_generation,
    run_qa_check,
    run_cybersecurity_check,
    run_deployment,
)
from apps.projects.models import Project
from django.db import transaction
from django.utils import timezone

class ApplaudePrimeAgent(BaseAgent):
    """
    The main orchestrator agent that interacts with the user,
    manages project lifecycle, and coordinates other specialized agents.
    """
    def __init__(self, user=None):
        super().__init__(
            agent_name="Applaude Prime",
            agent_persona="An AI agent that guides users through app creation by interacting directly, gathering requirements, and orchestrating other agents.",
            goal="To assist users in creating apps by managing the multi-agent workflow and project lifecycle."
        )
        self.user = user

    def execute(self, user_message: str, current_project_id=None, user=None):
        """
        Main method to process user messages, update project state,
        and trigger async tasks for specialized agents.

        Args:
            user_message (str): The message from the user.
            current_project_id (UUID or None): The current project ID if any.
            user (User): The Django user object.

        Returns:
            response (str): The AI agent's response to the user.
            project_id (UUID or None): The current or new project ID.
        """
        if current_project_id:
            try:
                project = Project.objects.get(id=current_project_id)
            except Project.DoesNotExist:
                project = None
        else:
            project = None

        if not project:
            # Create new project
            with transaction.atomic():
                timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
                unique_name = f"Project_{timestamp}"

                project = Project.objects.create(
                    owner=user,
                    name=unique_name,
                    status=Project.ProjectStatus.PENDING,
                    status_message="Project created. Awaiting market analysis.",
                )

            # Generate natural welcome response
            prompt = f"""
            You are Applaude Prime, an AI assistant that helps users create mobile apps from websites.
            A new user has started a conversation. Welcome them warmly, explain that you've created a project for them,
            and ask them to provide the URL of the website they want to turn into an app.
            Keep the response friendly and engaging.
            """
            response = self.model.generate_content(prompt).text.strip()
            return response, project.id

        # Handle project status and trigger tasks accordingly
        if project.status == Project.ProjectStatus.PENDING:
            # Assume user_message contains the source URL
            with transaction.atomic():
                project.source_url = user_message.strip()
                project.status = Project.ProjectStatus.ANALYSIS_PENDING
                project.status_message = "Market analysis started."
                project.save()
            # Trigger market analysis async task
            run_market_analysis.delay(str(project.id))

            # Generate natural response
            prompt = f"""
            You are Applaude Prime, an AI assistant helping create mobile apps from websites.
            The user has provided a website URL: {user_message.strip()}.
            Acknowledge that you've received the URL, explain that you're starting market analysis,
            and let them know you'll update them when it's complete.
            Keep the response friendly and informative.
            """
            response = self.model.generate_content(prompt).text.strip()
            return response, project.id

        elif project.status == Project.ProjectStatus.ANALYSIS_COMPLETE:
            # Check user response
            if user_message.lower() in ['yes', 'y', 'continue', 'proceed']:
                # Trigger design task
                with transaction.atomic():
                    project.status = Project.ProjectStatus.DESIGN_PENDING
                    project.status_message = "Design task started."
                    project.save()
                run_design_task.delay(str(project.id))

                # Generate natural response
                prompt = """
                You are Applaude Prime, an AI assistant helping create mobile apps.
                The user has agreed to proceed with the design phase after market analysis completion.
                Respond enthusiastically, confirm that you're starting the design phase,
                and explain what will happen next.
                Keep the response friendly and engaging.
                """
                response = self.model.generate_content(prompt).text.strip()
                return response, project.id
            elif user_message.lower() in ['no', 'n', 'stop']:
                # Generate natural response
                prompt = """
                You are Applaude Prime, an AI assistant helping create mobile apps.
                The user has decided to pause the project after market analysis completion.
                Acknowledge their decision politely and let them know they can resume anytime.
                Keep the response friendly and supportive.
                """
                response = self.model.generate_content(prompt).text.strip()
                return response, project.id
            else:
                # Ask again
                prompt = """
                You are Applaude Prime, an AI assistant helping create mobile apps.
                Market analysis is complete, and you've created a user persona and brand palette.
                Ask the user if they want to proceed with the design phase.
                Keep the response friendly and informative.
                """
                response = self.model.generate_content(prompt).text.strip()
                return response, project.id

        elif project.status == Project.ProjectStatus.DESIGN_COMPLETE:
            # Trigger code generation task
            with transaction.atomic():
                project.status = Project.ProjectStatus.CODE_GENERATION
                project.status_message = "Code generation started."
                project.save()
            run_code_generation.delay(str(project.id))

            # Generate natural response
            prompt = """
            You are Applaude Prime, an AI assistant helping create mobile apps.
            The design phase has just been completed. Inform the user that you're now starting the code generation phase.
            Explain what code generation involves and keep the response friendly and engaging.
            """
            response = self.model.generate_content(prompt).text.strip()
            return response, project.id

        elif project.status == Project.ProjectStatus.CODE_GENERATION:
            # Trigger QA task
            with transaction.atomic():
                project.status = Project.ProjectStatus.QA_PENDING
                project.status_message = "QA task started."
                project.save()
            run_qa_check.delay(str(project.id))

            # Generate natural response
            prompt = """
            You are Applaude Prime, an AI assistant helping create mobile apps.
            Code generation has been completed. Now starting the QA (Quality Assurance) phase.
            Explain what QA involves and reassure the user that you're ensuring high quality.
            Keep the response friendly and informative.
            """
            response = self.model.generate_content(prompt).text.strip()
            return response, project.id

        elif project.status == Project.ProjectStatus.QA_COMPLETE:
            # Trigger cybersecurity check
            with transaction.atomic():
                project.status_message = "Security analysis started."
                project.save()
            run_cybersecurity_check.delay(str(project.id))

            # Generate natural response
            prompt = """
            You are Applaude Prime, an AI assistant helping create mobile apps.
            QA is complete. Now performing a security analysis to ensure the app is safe.
            Explain the importance of security and keep the response reassuring.
            """
            response = self.model.generate_content(prompt).text.strip()
            return response, project.id

        elif project.status == Project.ProjectStatus.DEPLOYMENT_PENDING:
            # Trigger deployment task
            with transaction.atomic():
                project.status_message = "Deployment started."
                project.save()
            run_deployment.delay(str(project.id))

            # Generate natural response
            prompt = """
            You are Applaude Prime, an AI assistant helping create mobile apps.
            All checks are complete, and deployment is now in progress.
            Explain what deployment means and what the user can expect next.
            Keep the response exciting and positive.
            """
            response = self.model.generate_content(prompt).text.strip()
            return response, project.id

        elif project.status == Project.ProjectStatus.COMPLETED:
            # Generate natural response
            prompt = """
            You are Applaude Prime, an AI assistant helping create mobile apps.
            The project is now complete! Congratulate the user and explain how they can access their new app.
            Keep the response celebratory and helpful.
            """
            response = self.model.generate_content(prompt).text.strip()
            return response, project.id

        elif project.status == Project.ProjectStatus.FAILED:
            # Generate natural response
            prompt = """
            You are Applaude Prime, an AI assistant helping create mobile apps.
            Unfortunately, there was an issue with the project. Apologize and offer to help troubleshoot or start over.
            Keep the response supportive and solution-oriented.
            """
            response = self.model.generate_content(prompt).text.strip()
            return response, project.id

        else:
            # Generate natural response
            prompt = f"""
            You are Applaude Prime, an AI assistant helping create mobile apps.
            The current project status is {project.status}.
            Inform the user to please wait for the process to complete, and reassure them that you're working on it.
            Keep the response patient and encouraging.
            """
            response = self.model.generate_content(prompt).text.strip()
            return response, project.id
