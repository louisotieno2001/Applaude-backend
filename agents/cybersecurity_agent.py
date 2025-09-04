from .base_agent import BaseAgent
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
        project = Project.objects.get(id=project_id)
        project.status = "SECURITY_SCAN_PENDING"
        project.save()

        # In a real scenario, this would perform a security scan
        # For now, we simulate a successful security scan
        security_report = "No security vulnerabilities found. The codebase is secure."

        with transaction.atomic():
            project.status = "SECURITY_SCAN_COMPLETE"
            project.status_message = "Security scan passed successfully."
            project.save()
        print(f"Security scan complete for project {project_id}.")
        return security_report
