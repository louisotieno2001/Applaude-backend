from .base_agent_anthropic import BaseAgent
from apps.projects.models import Project
from django.db import transaction
import json

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

        if project.source_url and project.source_url.startswith('http'):
            task_description = f"""
            Objective: Extract the brand color palette from the website at {project.source_url}.

            Chain of Thought (CoT) Process:
            1. Understand Website Purpose: Briefly describe the main purpose or industry of the website at {project.source_url}. What kind of visual impression is it trying to make (e.g., minimalist, vibrant, corporate, playful)?
            2. Identify Primary Color: What is the most dominant color used for major elements like calls-to-action, prominent headers, or key graphical elements? Provide its hex code. If none is clearly dominant, infer a primary color that would fit the brand's purpose.
            3. Identify Secondary Color: What is the second most prominent color, often used for accents, secondary buttons, or complementary elements? Provide its hex code. If none is distinct, infer a complementary secondary color.
            4. Identify Light Text Color: What color is used for text that sits on dark backgrounds, ensuring high contrast and readability? Provide its hex code. If not explicit, assume a common light text color.
            5. Identify Dark Text Color: What color is used for text that sits on light backgrounds, ensuring high contrast and readability? Provide its hex code. If not explicit, assume a common dark text color.
            6. Identify Background Color: What is the most prevalent background color of the main content areas? Provide its hex code. If multiple backgrounds exist, choose the most dominant one for content.
            7. Final JSON Output: Based on the above analysis, construct a JSON object containing the identified colors.

            Output Requirements:
            - The response MUST be a valid JSON object.
            - The JSON object MUST contain the following keys: primary, secondary, text_light, text_dark, background.
            - Each color value MUST be a hexadecimal color code (e.g., "#RRGGBB").
            - If a specific color cannot be confidently identified from the website, provide a sensible default fallback hex code for that key (e.g., "#FFFFFF" for text_light if a light text color isn't obvious, "#000000" for text_dark, or "#F8F8F8" for background).
            - DO NOT include any text outside the JSON object (no introductory phrases like "Here is the JSON," no concluding remarks).
            - Here is an example of the desired JSON structure:
                {{
                  "primary": "#4A90E2",
                  "secondary": "#F5A623",
                  "text_light": "#FFFFFF",
                  "text_dark": "#333333",
                  "background": "#F8F9FA"
                }}

            Begin your Chain of Thought and then output the final JSON.
            """
        else:
            task_description = f"""
            Objective: Generate a suitable brand color palette based on the app description: "{project.source_url}".

            Chain of Thought (CoT) Process:
            1. Understand App Purpose: Briefly describe the main purpose or industry implied by the description "{project.source_url}". What kind of visual impression would suit it (e.g., minimalist, vibrant, corporate, playful)?
            2. Suggest Primary Color: Choose a dominant color that fits the app's theme for major elements like calls-to-action or headers. Provide its hex code.
            3. Suggest Secondary Color: Choose a complementary color for accents and secondary elements. Provide its hex code.
            4. Suggest Light Text Color: Choose a color for text on dark backgrounds, ensuring high contrast. Provide its hex code.
            5. Suggest Dark Text Color: Choose a color for text on light backgrounds, ensuring high contrast. Provide its hex code.
            6. Suggest Background Color: Choose a suitable background color for main content areas. Provide its hex code.
            7. Final JSON Output: Construct a JSON object containing the suggested colors.

            Output Requirements:
            - The response MUST be a valid JSON object.
            - The JSON object MUST contain the following keys: primary, secondary, text_light, text_dark, background.
            - Each color value MUST be a hexadecimal color code (e.g., "#RRGGBB").
            - DO NOT include any text outside the JSON object.
            - Here is an example of the desired JSON structure:
                {{
                  "primary": "#4A90E2",
                  "secondary": "#F5A623",
                  "text_light": "#FFFFFF",
                  "text_dark": "#333333",
                  "background": "#F8F9FA"
                }}

            Begin your Chain of Thought and then output the final JSON.
            """

        full_prompt = self._generate_prompt(task_description)

        try:
            # Use Anthropic API call through BaseAgent's model
            generated_json_text = self.generate_content(full_prompt)

            # Extract the JSON block from the response
            import re
            json_match = re.search(r'```json\n({.*?})\n```', generated_json_text, re.DOTALL)
            if json_match:
                parsed_palette = json.loads(json_match.group(1))
            else:
                # Try to parse the entire response as JSON if no code block found
                try:
                    parsed_palette = json.loads(generated_json_text.strip())
                except json.JSONDecodeError:
                    raise ValueError("Could not extract JSON from Anthropic response.")

            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.brand_palette = parsed_palette
                project.status = Project.ProjectStatus.DESIGN_COMPLETE
                project.status_message = "Design analysis complete. Brand palette generated."
                project.save()

            self.send_status_notification(project)

            print(f"Design analysis complete for project {project_id}. Palette extracted: {parsed_palette}")

        except Exception as e:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.FAILED
                project.status_message = f"Design analysis failed: {e}"
                project.save()
            print(f"Error during design analysis for project {project_id}: {e}")
            raise
