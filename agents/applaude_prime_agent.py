from .base_agent_anthropic import BaseAgent
from apps.projects.tasks import (
    run_market_analysis,
    run_design_task,
    run_code_generation,
    run_qa_check,
    run_cybersecurity_check,
    run_deployment,
    send_project_status_notification,
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
            You are Applaude Prime, an AI assistant that helps users create mobile apps from websites or app ideas.
            A new user has started a conversation. Welcome them warmly and engagingly. Explain that you've created a new project for them called '{project.name}'.
            To get started, ask them to either provide a website URL to convert into a mobile app, or describe the app they want to build in detail (e.g., "Create a simple to-do app with task lists and reminders").
            Make it clear that they should provide a description or URL now to proceed.
            Keep the response friendly, dynamic, and guide them on what to do next. Do not use asterisks, bold, or any markdown formatting. Keep it plain text.
            """
            response = self.generate_content(prompt).strip()
            return response, project.id

        # Handle project status and trigger tasks accordingly
        if project.status == Project.ProjectStatus.PENDING:
            # Assume user_message contains the source URL
            with transaction.atomic():
                project.source_url = user_message.strip()
                project.status = Project.ProjectStatus.ANALYSIS_PENDING
                project.status_message = "Market analysis started."
                project.save()
            send_project_status_notification(project)
            # Trigger market analysis async task
            run_market_analysis.delay(str(project.id))

            # Generate natural response
            prompt = f"""
            You are Applaude Prime, an AI assistant helping create mobile apps from websites or app ideas.
            The user has provided input: "{user_message.strip()}".
            Acknowledge enthusiastically that you've received their input and started the project.
            Explain that you're now beginning market analysis to understand the target audience and create a user persona.
            Let them know this step will take a few moments, and you'll notify them when it's done with the results.
            Keep the response friendly, dynamic, and reassuring - no need for them to respond yet. Do not use asterisks, bold, or any markdown formatting. Keep it plain text.
            """
            response = self.generate_content(prompt).strip()
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
                prompt = f"""
                You are Applaude Prime, an AI assistant helping create mobile apps.
                The user has agreed to proceed with the design phase after market analysis completion.
                Respond enthusiastically, confirm that you're starting the design phase to create UI/UX designs and extract/generate a brand color palette.
                Explain that this will take a bit, and you'll update them when it's ready for the next step.
                Keep the response friendly, dynamic, and informative - no user action needed now. Do not use asterisks, bold, or any markdown formatting. Keep it plain text.
                """
                response = self.generate_content(prompt).strip()
                return response, project.id
            elif user_message.lower() in ['no', 'n', 'stop']:
                # Generate natural response
                prompt = f"""
                You are Applaude Prime, an AI assistant helping create mobile apps.
                The user has decided to pause the project after market analysis completion.
                Acknowledge their decision politely, summarize what was accomplished (user persona and brand palette created), and let them know they can resume anytime by saying 'yes' or 'continue'.
                Keep the response friendly and supportive. Do not use asterisks, bold, or any markdown formatting. Keep it plain text.
                """
                response = self.generate_content(prompt).strip()
                return response, project.id
            else:
                # Ask again
                prompt = f"""
                You are Applaude Prime, an AI assistant helping create mobile apps.
                Market analysis is complete! I've created a detailed user persona and brand color palette based on your input.
                Now, ask the user clearly if they want to proceed to the design phase (where I'll create UI/UX designs).
                Explain that if they say 'yes', we'll move forward; if 'no', we can pause and resume later.
                Make it dynamic and guide them on what to respond.
                Keep the response friendly and informative. Do not use asterisks, bold, or any markdown formatting. Keep it plain text.
                """
                response = self.generate_content(prompt).strip()
                return response, project.id

        elif project.status == Project.ProjectStatus.DESIGN_COMPLETE:
            # Trigger code generation task
            with transaction.atomic():
                project.status = Project.ProjectStatus.CODE_GENERATION
                project.status_message = "Code generation started."
                project.save()
            run_code_generation.delay(str(project.id))

            # Generate natural response
            prompt = f"""
            You are Applaude Prime, an AI assistant helping create mobile apps.
            The design phase has just been completed! I've created UI/UX designs and a brand color palette.
            Now, inform the user that you're starting the code generation phase, where I'll build the actual mobile app code based on the designs and persona.
            Explain that this is a big step and will take some time, but they'll get a fully functional app.
            Keep the response friendly, dynamic, and exciting - no user action needed now. Do not use asterisks, bold, or any markdown formatting. Keep it plain text.
            """
            response = self.generate_content(prompt).strip()
            return response, project.id

        elif project.status == Project.ProjectStatus.CODE_GENERATION:
            # Trigger QA task
            with transaction.atomic():
                project.status = Project.ProjectStatus.QA_PENDING
                project.status_message = "QA task started."
                project.save()
            run_qa_check.delay(str(project.id))

            # Generate natural response
            prompt = f"""
            You are Applaude Prime, an AI assistant helping create mobile apps.
            Code generation has been completed! I've built the full mobile app code.
            Now, inform the user that you're starting the QA (Quality Assurance) phase to test and ensure the app works perfectly.
            Explain that QA involves checking for bugs, performance, and usability.
            Keep the response friendly, dynamic, and reassuring - no user action needed now. Do not use asterisks, bold, or any markdown formatting. Keep it plain text.
            """
            response = self.generate_content(prompt).strip()
            return response, project.id

        elif project.status == Project.ProjectStatus.QA_COMPLETE:
            # Trigger cybersecurity check
            with transaction.atomic():
                project.status_message = "Security analysis started."
                project.save()
            run_cybersecurity_check.delay(str(project.id))

            # Generate natural response
            prompt = f"""
            You are Applaude Prime, an AI assistant helping create mobile apps.
            QA is complete! The app has passed all quality checks.
            Now, inform the user that you're performing a comprehensive security analysis to ensure the app is safe and secure.
            Explain that this checks for vulnerabilities and best practices.
            Keep the response friendly, dynamic, and reassuring - no user action needed now. Do not use asterisks, bold, or any markdown formatting. Keep it plain text.
            """
            response = self.generate_content(prompt).strip()
            return response, project.id

        elif project.status == Project.ProjectStatus.DEPLOYMENT_PENDING:
            # Trigger deployment task
            with transaction.atomic():
                project.status_message = "Deployment started."
                project.save()
            run_deployment.delay(str(project.id))

            # Generate natural response
            prompt = f"""
            You are Applaude Prime, an AI assistant helping create mobile apps.
            Security analysis is complete! The app is secure and ready.
            Now, inform the user that deployment is starting - this means packaging the app and making it available for download.
            Explain that once done, they'll get a download link for their fully built mobile app.
            Keep the response exciting, positive, and dynamic - no user action needed now. Do not use asterisks, bold, or any markdown formatting. Keep it plain text.
            """
            response = self.generate_content(prompt).strip()
            return response, project.id

        elif project.status == Project.ProjectStatus.COMPLETED:
            # Generate natural response
            download_link = project.generated_code_path or f"https://cdn.applaude.ai/apps/{project.id}/app.apk"
            prompt = f"""
            You are Applaude Prime, an AI assistant helping create mobile apps.
            The project is now complete! Congratulate the user enthusiastically on their new mobile app.
            Provide them with the download link: {download_link}
            Explain that they can download the app source code or APK from this link.
            Keep the response celebratory, helpful, and dynamic. Do not use asterisks, bold, or any markdown formatting. Keep it plain text.
            """
            response = self.generate_content(prompt).strip()
            return response, project.id

        elif project.status == Project.ProjectStatus.FAILED:
            # Generate natural response
            prompt = f"""
            You are Applaude Prime, an AI assistant helping create mobile apps.
            Unfortunately, there was an issue with the project: {project.status_message}.
            Apologize sincerely and offer to help troubleshoot or start a new project.
            Keep the response supportive, solution-oriented, and dynamic. Do not use asterisks, bold, or any markdown formatting. Keep it plain text.
            """
            response = self.generate_content(prompt).strip()
            return response, project.id

        else:
            # Generate natural response
            prompt = f"""
            You are Applaude Prime, an AI assistant helping create mobile apps.
            The current project status is {project.status}: {project.status_message}.
            Inform the user that the process is ongoing and reassure them that you're working on it.
            Keep the response patient, encouraging, and dynamic. Do not use asterisks, bold, or any markdown formatting. Keep it plain text.
            """
            response = self.generate_content(prompt).strip()
            return response, project.id
