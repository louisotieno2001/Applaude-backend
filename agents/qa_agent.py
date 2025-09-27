from .base_agent_anthropic import BaseAgent
from apps.projects.models import Project
from django.db import transaction
from .prompts.super_prompts import QA_ENGINEER_PERSONA, QA_ENGINEER_GOAL

class QAAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="QA Engineer",
            agent_persona=QA_ENGINEER_PERSONA,
            goal=QA_ENGINEER_GOAL
        )

    def execute(self, project_id: int):
        print(f"Executing QA Agent for project {project_id}...")

        try:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)

                # Ensure we have generated code to analyze
                if not project.generated_code:
                    raise Exception("Cannot perform QA: Generated code is missing.")

                project.status = Project.ProjectStatus.QA_PENDING
                project.status_message = "Performing comprehensive quality assurance analysis..."
                project.save()

        except Project.DoesNotExist:
            print(f"Error: Project with ID {project_id} not found.")
            return
        except Exception as e:
            print(f"Error: {e}")
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.FAILED
                project.status_message = f"QA analysis failed: {e}"
                project.save()
            return

        # Construct the comprehensive QA analysis task for Vertex AI
        task_description = f"""
        **MISSION: Perform Comprehensive Quality Assurance Analysis**

        **Project Context:**
        - **Project Name:** {project.name}
        - **App Type:** {project.app_type}
        - **Source Input:** {project.source_url}

        **Generated Code to Analyze:**
        {project.generated_code}

        **Quality Assurance Framework:**

        **1. Static Code Analysis:**
        - Review code structure and organization
        - Check for proper imports and dependencies
        - Identify potential null pointer exceptions or runtime errors
        - Verify adherence to platform-specific best practices
        - Assess code readability and maintainability

        **2. Security Audit:**
        - Check for common security vulnerabilities
        - Identify hardcoded secrets or sensitive data
        - Assess input validation and sanitization
        - Review authentication and authorization patterns
        - Check for proper error handling

        **3. Performance Review:**
        - Identify potential performance bottlenecks
        - Check for inefficient algorithms or data structures
        - Assess memory management patterns
        - Review network request patterns
        - Identify potential memory leaks or resource issues

        **4. User Experience Assessment:**
        - Evaluate UI/UX consistency
        - Check for accessibility considerations
        - Assess error handling and user feedback
        - Review navigation and user flow
        - Identify potential usability issues

        **5. Code Quality Standards:**
        - Check for code duplication
        - Assess testability of components
        - Review documentation and comments
        - Verify proper separation of concerns
        - Check for adherence to coding standards

        **Output Requirements:**
        Generate a detailed QA report in Markdown format with the following structure:

        # QA Analysis Report for {project.name}

        ## Executive Summary
        [Overall assessment of code quality]

        ## Issues Found

        ### Critical Issues
        [List any critical issues that must be fixed]

        ### High Priority Issues
        [List high priority issues]

        ### Medium Priority Issues
        [List medium priority issues]

        ### Low Priority Issues
        [List low priority issues]

        ## Security Assessment
        [Security findings and recommendations]

        ## Performance Analysis
        [Performance findings and recommendations]

        ## Recommendations
        [Overall recommendations for improvement]

        **Final Assessment:**
        [Overall pass/fail recommendation]
        """

        full_prompt = self._generate_prompt(task_description)

        try:
            # Use Anthropic API call through BaseAgent's model
            qa_report = self.generate_content(full_prompt)

            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.qa_report = qa_report
                project.status = Project.ProjectStatus.QA_COMPLETE
                project.status_message = "QA analysis complete. Comprehensive quality assessment generated."
                project.save()

            self.send_status_notification(project)

            print(f"QA analysis complete for project {project_id}. Report generated.")
            return qa_report

        except Exception as e:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.FAILED
                project.status_message = f"QA analysis failed: {e}"
                project.save()
            print(f"Error during QA analysis for project {project_id}: {e}")
            raise
