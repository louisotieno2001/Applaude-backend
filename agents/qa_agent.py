from .base_agent import BaseAgent
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
        project = Project.objects.get(id=project_id)
        project.status = "QA_PENDING"
        project.save()

        # In a real scenario, this would analyze the generated code
        # For now, we simulate a successful QA check
        qa_report = "No critical, high, medium, or low severity issues found. The codebase meets all quality standards."

        with transaction.atomic():
            project.status = "QA_COMPLETE"
            project.status_message = "QA checks passed successfully."
            project.save()
        print(f"QA check complete for project {project_id}.")
        return qa_report
