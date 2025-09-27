from .base_agent_anthropic import BaseAgent
from .prompts.super_prompts import MARKET_ANALYST_PERSONA, MARKET_ANALYST_GOAL
from apps.projects.models import Project
from django.db import transaction

class MarketAnalystAgent(BaseAgent):
    """
    Analyzes a user's website to generate a detailed user persona.
    """
    def __init__(self):
        super().__init__(
            agent_name="Market Analyst",
            agent_persona=MARKET_ANALYST_PERSONA,
            goal=MARKET_ANALYST_GOAL
        )

    def execute(self, project_id: int):
        """
        Performs the market analysis for a given project, leveraging the agent's
        ability to 'access' and thoroughly research the website.

        Args:
            project_id (int): The ID of the project to analyze.
        """
        print(f"Executing Market Analyst Agent for project {project_id}...")
        try:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status_message = "Initiating deep market and website analysis..."
                project.status = Project.ProjectStatus.ANALYSIS_PENDING
                project.save()
        except Project.DoesNotExist:
            print(f"Error: Project with ID {project_id} not found.")
            return

        # 1. Construct the detailed task for the Anthropic API, emphasizing comprehensive analysis
        if project.source_url and project.source_url.startswith('http'):
            task_description = f"""
            Mission: Conduct an exhaustive and nuanced market research analysis of the website at the provided URL: {project.source_url}. Your analysis must be driven by the ultimate goal of developing a world-class mobile application that serves this website's audience.

            Deep Dive Analysis Points:
            - Website Core Functionality: What are the primary features and functionalities offered by the website? How are they presented?
            - Target User Behavior & Flow: Based on the website's design and content, infer the typical user journey, their potential goals, and pain points when interacting with the site.
            - Aesthetic & Branding Elements: Analyze the visual identity, including color schemes, typography, and especially the logo. What emotions or brand values does the logo convey? How does the overall aesthetic contribute to user perception?
            - Perceived Performance & User Experience (UX): While you cannot directly measure speed, infer perceived performance based on loading cues, design responsiveness, and overall fluidity of navigation. What aspects of the current UX are strong, and where might a mobile app enhance it?
            - Content Types & Structure: What kind of content is dominant? How is it organized? (e.g., articles, products, services, portfolio items).
            - Monetization/Value Proposition: How does the website generate value or revenue? What is its unique selling proposition?
            - Implicit Codebase Insights (from user-facing experience): While not analyzing raw code, infer potential underlying technology characteristics based on observable features (e.g., dynamic content suggests API interactions, complex forms imply robust backend).

            Deliverable: Based on this exhaustive analysis, generate a comprehensive, highly detailed, and actionable user persona document. The document MUST be formatted in clean Markdown and include a memorable and representative name for the persona (e.g., 'Savvy Sarah', 'Tech-Forward Tom'). Emphasize how the mobile app can uniquely solve their problems or enhance their experience beyond the current website.
            """
        else:
            task_description = f"""
            Mission: Based on the app description: "{project.source_url}", conduct market research and analysis to develop a world-class mobile application that fits this concept.

            Analysis Points:
            - App Concept Interpretation: Understand the core idea and functionality implied by the description.
            - Target User Behavior & Flow: Infer the typical user journey, their potential goals, and pain points for such an app.
            - Aesthetic & Branding Elements: Suggest visual identity, color schemes, and branding that would suit the app concept.
            - User Experience (UX): Think about how the mobile app can provide a great user experience for the described functionality.
            - Content Types & Structure: What kind of content or features would be dominant in such an app?
            - Value Proposition: What unique selling points can the app offer?

            Deliverable: Generate a comprehensive, highly detailed, and actionable user persona document. The document MUST be formatted in clean Markdown and include a memorable and representative name for the persona (e.g., 'Savvy Sarah', 'Tech-Forward Tom'). Emphasize how the mobile app can fulfill the described concept and solve user problems.
            """

        full_prompt = self._generate_prompt(task_description)

        try:
            # 2. Call the Anthropic API for comprehensive analysis using BaseAgent's model
            persona_document = self.generate_content(full_prompt)

            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.user_persona_document = persona_document
                project.status = Project.ProjectStatus.ANALYSIS_COMPLETE
                project.status_message = "Market analysis complete. Comprehensive user persona generated."
                project.save()

            self.send_status_notification(project)

            print(f"Market Analysis complete for project {project_id}. Persona generated reflecting deep insights.")

        except Exception as e:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.FAILED
                project.status_message = f"Market analysis failed: {e}"
                project.save()
            print(f"Error during market analysis for project {project_id}: {e}")
            raise
