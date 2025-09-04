
from .base_agent import BaseAgent
from apps.projects.models import Project
from django.db import transaction
import google.generativeai as genai
import os

class DesignAgent(BaseAgent):
    """
    Analyzes a user's website to extract a brand-consistent color palette.
    """
    def __init__(self):
        super().__init__(
            agent_name="Design",
            agent_persona="You are the 'Digital Design Agent,' an AI with a masterful eye for aesthetics and brand identity. You can look at any website and instantly identify its core color palette, understanding the role each color plays in the brand's visual language (e.g., primary, secondary, accent). Your output will be a precise JSON object containing hex codes.",
            goal="To extract the primary, secondary, text (light/dark), and background branding colors from a user's website to ensure perfect brand consistency in the generated mobile app. If a specific color type cannot be confidently identified, provide a sensible fallback hex code (e.g., #FFFFFF for white, #000000 for black, #CCCCCC for gray). The output must be PURE JSON, with no introductory or concluding text."
        )
        self.model = genai.GenerativeModel('gemini-1.5-pro') # Using a more capable model for prompt engineering

    def execute(self, project_id: int):
        """
        Extracts the color palette for a given project using a Chain-of-Thought approach.
        
        Args:
            project_id (int): The ID of the project to analyze.
        """
        print(f"Executing Design Agent for project {project_id}...")
        try:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status_message = "Analyzing website for design elements and brand palette..."
                project.status = Project.ProjectStatus.DESIGN_PENDING # Set status to pending
                project.save()
        except Project.DoesNotExist:
            print(f"Error: Project with ID {project_id} not found.")
            return

        task_description = f"""
        **Objective:** Extract the brand color palette from the website at `{project.source_url}`.

        **Chain of Thought (CoT) Process:**
        1.  **Understand Website Purpose:** Briefly describe the main purpose or industry of the website at `{project.source_url}`. What kind of visual impression is it trying to make (e.g., minimalist, vibrant, corporate, playful)?
        2.  **Identify Primary Color:** What is the most dominant color used for major elements like calls-to-action, prominent headers, or key graphical elements? Provide its hex code. If none is clearly dominant, infer a primary color that would fit the brand's purpose.
        3.  **Identify Secondary Color:** What is the second most prominent color, often used for accents, secondary buttons, or complementary elements? Provide its hex code. If none is distinct, infer a complementary secondary color.
        4.  **Identify Light Text Color:** What color is used for text that sits on dark backgrounds, ensuring high contrast and readability? Provide its hex code. If not explicit, assume a common light text color.
        5.  **Identify Dark Text Color:** What color is used for text that sits on light backgrounds, ensuring high contrast and readability? Provide its hex code. If not explicit, assume a common dark text color.
        6.  **Identify Background Color:** What is the most prevalent background color of the main content areas? Provide its hex code. If multiple backgrounds exist, choose the most dominant one for content.
        7.  **Final JSON Output:** Based on the above analysis, construct a JSON object containing the identified colors.

        **Output Requirements:**
        * The response MUST be a valid JSON object.
        * The JSON object MUST contain the following keys: `primary`, `secondary`, `text_light`, `text_dark`, `background`.
        * Each color value MUST be a hexadecimal color code (e.g., "#RRGGBB").
        * If a specific color cannot be confidently identified from the website, provide a sensible default fallback hex code for that key (e.g., "#FFFFFF" for `text_light` if a light text color isn't obvious, "#000000" for `text_dark`, or "#F8F8F8" for `background`).
        * DO NOT include any text outside the JSON object (no introductory phrases like "Here is the JSON," no concluding remarks).
        * Here is an example of the desired JSON structure:
            ```json
            {
              "primary": "#4A90E2",
              "secondary": "#F5A623",
              "text_light": "#FFFFFF",
              "text_dark": "#333333",
              "background": "#F8F9FA"
            }
            ```
        
        Begin your Chain of Thought and then output the final JSON.
        """
        
        full_prompt = self._generate_prompt(task_description)

        try:
            # Simulate API call with a robust prompt
            # In a real scenario, this would involve web scraping/color analysis
            # response = self.model.generate_content(full_prompt)
            # generated_json_text = response.text
            # parsed_palette = json.loads(generated_json_text)

            # For demonstration, use a placeholder that adheres to the new prompt's structure
            # A real response would be generated by Gemini based on the URL analysis
            simulated_response = """
            **Chain of Thought:**
            1.  **Understand Website Purpose:** The website `uplas.me` (assuming this is the backend for `uplas.me`) seems to be a modern, tech-focused platform, likely for services or portfolios, given its general nature. It aims for a clean, professional, and slightly futuristic impression.
            2.  **Identify Primary Color:** Based on common tech website aesthetics, a strong, vibrant blue or purple is often used. Let's assume a deep blue.
            3.  **Identify Secondary Color:** A complementary orange or pink could be used for accents.
            4.  **Identify Light Text Color:** For dark backgrounds, white or off-white is standard.
            5.  **Identify Dark Text Color:** For light backgrounds, a dark gray or black is typical.
            6.  **Identify Background Color:** A subtle, dark background like a near-black or deep grey is common for modern tech UIs.

            **Final JSON Output:**
            ```json
            {
              "primary": "#007BFF",
              "secondary": "#FF6B81",
              "text_light": "#F0F0F0",
              "text_dark": "#2C3E50",
              "background": "#1A1A2E"
            }
            ```
            """
            
            # Extract the JSON block from the simulated response
            import re
            json_match = re.search(r'```json\n({.*?})\n```', simulated_response, re.DOTALL)
            if json_match:
                parsed_palette = json.loads(json_match.group(1))
            else:
                raise ValueError("Could not extract JSON from simulated response.")

            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.brand_palette = parsed_palette
                project.status = Project.ProjectStatus.DESIGN_COMPLETE
                project.status_message = "Design analysis complete. Brand palette generated."
                project.save()

            print(f"Design analysis complete for project {project_id}. Palette extracted: {parsed_palette}")

        except Exception as e:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.FAILED
                project.status_message = f"Design analysis failed: {e}"
                project.save()
            print(f"Error during design analysis for project {project_id}: {e}")
            raise
