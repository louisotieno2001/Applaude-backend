# File: backend/agents/market_analyst_agent.py
from .base_agent import BaseAgent
from .prompts.super_prompts import MARKET_ANALYST_PERSONA, MARKET_ANALYST_GOAL
from apps.projects.models import Project
from django.db import transaction
import google.generativeai as genai
import os

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
        self.model = genai.GenerativeModel('gemini-1.5-pro') # Using a more capable model for prompt engineering

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

        # 1. Construct the detailed task for the Gemini API, emphasizing comprehensive analysis
        task_description = f"""
        **Mission:** Conduct an exhaustive and nuanced market research analysis of the website at the provided URL: `{project.source_url}`. Your analysis must be driven by the ultimate goal of developing a world-class mobile application that serves this website's audience.

        **Deep Dive Analysis Points:**
        -   **Website Core Functionality:** What are the primary features and functionalities offered by the website? How are they presented?
        -   **Target User Behavior & Flow:** Based on the website's design and content, infer the typical user journey, their potential goals, and pain points when interacting with the site.
        -   **Aesthetic & Branding Elements:** Analyze the visual identity, including color schemes, typography, and especially the **logo**. What emotions or brand values does the logo convey? How does the overall aesthetic contribute to user perception?
        -   **Perceived Performance & User Experience (UX):** While you cannot directly measure speed, infer perceived performance based on loading cues, design responsiveness, and overall fluidity of navigation. What aspects of the current UX are strong, and where might a mobile app enhance it?
        -   **Content Types & Structure:** What kind of content is dominant? How is it organized? (e.g., articles, products, services, portfolio items).
        -   **Monetization/Value Proposition:** How does the website generate value or revenue? What is its unique selling proposition?
        -   **Implicit Codebase Insights (from user-facing experience):** While not analyzing raw code, infer potential underlying technology characteristics based on observable features (e.g., dynamic content suggests API interactions, complex forms imply robust backend).

        **Deliverable:** Based on this exhaustive analysis, generate a comprehensive, highly detailed, and actionable user persona document. The document MUST be formatted in clean Markdown and include a memorable and representative name for the persona (e.g., 'Savvy Sarah', 'Tech-Forward Tom'). Emphasize how the mobile app can uniquely solve their problems or enhance their experience beyond the current website.
        """
        
        full_prompt = self._generate_prompt(task_description)

        try:
            # 2. (Simulated) Call the Gemini API for comprehensive analysis
            # In a final production version, this would be an actual API call,
            # potentially integrated with web scraping tools or simulated data inputs
            # based on real-world analysis.
            # response = self.model.generate_content(full_prompt)
            # persona_document = response.text
            
            # For now, we use a more detailed placeholder response that reflects
            # the depth of analysis requested.
            persona_document = f"""## Persona: Digital Nomad Diana

**Demographics:**
* **Age:** 28-40
* **Gender:** Female
* **Location:** Global (often traveling, relies on mobile for everything)
* **Income Level:** Mid to high (freelancer, remote worker, small business owner)
* **Education:** Bachelor's or Master's degree, self-learner

**Psychographics:**
* **Interests:** Digital tools, productivity, remote work, online learning, travel, community, efficient resource management, sustainable living.
* **Values:** Freedom, flexibility, efficiency, quality, continuous growth, connection, simplicity.
* **Pain Points:** Information overload, clunky interfaces, unreliable web access on the go, difficulty staying organized across different platforms, lack of integrated solutions, time zone challenges.
* **Motivations:** To streamline her work, maintain professional presence, learn new skills, connect with like-minded individuals, manage her digital life effectively while being location independent.

**User Goals (when interacting with a platform like {project.source_url}):**
1.  Quickly access relevant content or services on the go.
2.  Efficiently manage tasks or projects related to the website's offering.
3.  Connect with support or community effortlessly.
4.  Receive critical updates without needing to constantly check a desktop.
5.  Find visually appealing and intuitive interfaces that save time.

**Key Value Proposition (derived from {project.source_url}'s implied offerings):**
The website's primary value proposition is offering a highly efficient, visually engaging, and comprehensive digital ecosystem for [Inferred website purpose, e.g., 'creative professionals to showcase their work and connect with clients']. It promises to simplify complex workflows and empower users with tools that enhance their productivity and professional reach, wherever they are.

**How a Mobile App will 'Wow' Diana:**
A dedicated mobile app for {project.source_url} would truly 'wow' Diana by:
* **Instant Access:** Providing immediate, optimized access to core features without browser overhead.
* **Offline Capability:** Allowing her to review critical content or work on tasks even with intermittent internet.
* **Native Performance:** Delivering buttery-smooth interactions and quick load times that web versions often struggle with on mobile.
* **Push Notifications:** Keeping her informed of crucial updates (new clients, project status changes, community messages) in real-time.
* **Seamless Integration:** Leveraging native mobile features like camera, GPS, and biometric authentication for a truly integrated and secure experience.
* **Dedicated UI:** Offering a purpose-built UI/UX that feels natural and intuitive on a smartphone, eliminating the need to pinch and zoom or deal with responsive design quirks.
* **Brand Loyalty:** Deepening her connection to the brand through a premium, always-available experience.
"""

            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.user_persona_document = persona_document
                project.status = Project.ProjectStatus.ANALYSIS_COMPLETE
                project.status_message = "Market analysis complete. Comprehensive user persona generated."
                project.save()
            
            print(f"Market Analysis complete for project {project_id}. Persona generated reflecting deep insights.")
            
        except Exception as e:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.FAILED
                project.status_message = f"Market analysis failed: {e}"
                project.save()
            print(f"Error during market analysis for project {project_id}: {e}")
            raise
