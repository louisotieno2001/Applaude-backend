from .base_agent_anthropic import BaseAgent
from apps.projects.models import Project
from django.db import transaction
from .prompts.super_prompts import CYBERSECURITY_AGENT_PERSONA, CYBERSECURITY_AGENT_GOAL

class CybersecurityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="Cybersecurity Sentinel",
            agent_persona=CYBERSECURITY_AGENT_PERSONA,
            goal=CYBERSECURITY_AGENT_GOAL
        )

    def execute(self, project_id: int):
        print(f"Executing Cybersecurity Agent for project {project_id}...")

        try:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)

                # Ensure we have generated code to analyze
                if not project.generated_code:
                    raise Exception("Cannot perform security analysis: Generated code is missing.")

                project.status = Project.ProjectStatus.SECURITY_SCAN_PENDING
                project.status_message = "Performing comprehensive security analysis..."
                project.save()

        except Project.DoesNotExist:
            print(f"Error: Project with ID {project_id} not found.")
            return
        except Exception as e:
            print(f"Error: {e}")
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.FAILED
                project.status_message = f"Security analysis failed: {e}"
                project.save()
            return

        # Construct the comprehensive security analysis task for Vertex AI
        task_description = f"""
        **MISSION: Perform Comprehensive Security Analysis**

        **Project Context:**
        - **Project Name:** {project.name}
        - **App Type:** {project.app_type}
        - **Source Input:** {project.source_url}

        **Generated Code to Analyze:**
        {project.generated_code}

        **Security Analysis Framework:**

        **1. Static Application Security Testing (SAST):**
        - Analyze code for common vulnerabilities (OWASP Top 10)
        - Check for injection vulnerabilities (SQL, XSS, Command Injection)
        - Identify authentication and authorization flaws
        - Review session management patterns
        - Assess cryptographic implementations

        **2. Dependency Security Analysis:**
        - Review third-party libraries and dependencies
        - Check for known vulnerable components
        - Assess dependency chain security
        - Identify outdated or deprecated packages
        - Review license compliance

        **3. Data Security Assessment:**
        - Check for sensitive data exposure
        - Assess data validation and sanitization
        - Review data storage security
        - Check for proper encryption usage
        - Identify potential data leakage points

        **4. Network Security Review:**
        - Assess API security patterns
        - Check for secure communication protocols
        - Review network request handling
        - Identify potential man-in-the-middle vulnerabilities
        - Assess certificate and SSL/TLS usage

        **5. Mobile-Specific Security:**
        - Check for platform-specific vulnerabilities
        - Assess local storage security
        - Review biometric authentication usage
        - Check for proper permission handling
        - Assess jailbreak/root detection mechanisms

        **6. Compliance and Best Practices:**
        - Verify adherence to security frameworks
        - Check for proper error handling
        - Assess logging and monitoring patterns
        - Review incident response considerations
        - Check for security headers and configurations

        **Output Requirements:**
        Generate a detailed security report in Markdown format with the following structure:

        # Security Analysis Report for {project.name}

        ## Executive Summary
        [Overall security assessment and risk level]

        ## Critical Vulnerabilities
        [List any critical security issues that must be addressed immediately]

        ## High Risk Issues
        [List high-risk security vulnerabilities]

        ## Medium Risk Issues
        [List medium-risk security concerns]

        ## Low Risk Issues
        [List low-risk security findings]

        ## Security Recommendations
        [Specific recommendations for improving security]

        ## Compliance Assessment
        [Assessment against security standards and frameworks]

        **Overall Security Rating:**
        [Provide an overall security rating: CRITICAL, HIGH, MEDIUM, LOW]

        **Immediate Actions Required:**
        [List any immediate actions that must be taken]
        """

        full_prompt = self._generate_prompt(task_description)

        try:
            # Use Anthropic API call through BaseAgent's model
            security_report = self.generate_content(full_prompt)

            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.security_report = security_report
                project.status = Project.ProjectStatus.SECURITY_SCAN_COMPLETE
                project.status_message = "Security analysis complete. Comprehensive security assessment generated."
                project.save()

            self.send_status_notification(project)

            print(f"Security analysis complete for project {project_id}. Report generated.")
            return security_report

        except Exception as e:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.FAILED
                project.status_message = f"Security analysis failed: {e}"
                project.save()
            print(f"Error during security analysis for project {project_id}: {e}")
            raise
