from .base_agent_anthropic import BaseAgent
from .prompts.super_prompts import CODE_GEN_PERSONA, CODE_GEN_GOAL
from apps.projects.models import Project
from django.db import transaction
import json

class CodeGenerationAgent(BaseAgent):
    """
    Generates production-ready mobile application code based on user persona and design palette.
    """
    def __init__(self):
        super().__init__(
            agent_name="Code Generation",
            agent_persona=CODE_GEN_PERSONA,
            goal=CODE_GEN_GOAL
        )

    def execute(self, project_id: int):
        """
        Generates the complete mobile application code for a given project.

        Args:
            project_id (int): The ID of the project to generate code for.
        """
        print(f"Executing Code Generation Agent for project {project_id}...")

        try:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)

                # Ensure we have the required data before generating code
                if not project.user_persona_document:
                    raise Exception("Cannot generate code: User persona document is missing.")
                if not project.brand_palette:
                    raise Exception("Cannot generate code: Brand palette is missing.")

                project.status = Project.ProjectStatus.CODE_GENERATION
                project.status_message = "Generating production-ready mobile application code..."
                project.save()

        except Project.DoesNotExist:
            print(f"Error: Project with ID {project_id} not found.")
            return
        except Exception as e:
            print(f"Error: {e}")
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.FAILED
                project.status_message = f"Code generation failed: {e}"
                project.save()
            return

        # Construct the comprehensive task for the Vertex AI API
        task_description = f"""
        **MISSION: Generate Complete Production-Ready Mobile Application Code**

        **Project Context:**
        - **Project Name:** {project.name}
        - **App Type:** {project.app_type}
        - **Source Input:** {project.source_url}

        **User Persona Document:**
        {project.user_persona_document}

        **Brand Palette:**
        {json.dumps(project.brand_palette, indent=2)}

        **Code Generation Requirements:**

        **1. Architecture & Technology Stack:**
        - Choose the most appropriate framework for the app type: React Native (cross-platform), Flutter (cross-platform), or native iOS/Android
        - Design a scalable, maintainable architecture
        - Include proper state management, API integration patterns, and navigation structure

        **2. File Structure:**
        Create a logical, production-ready file structure with the following components:
        - Main application files (App.js, main.dart, etc.)
        - Screen/View components
        - Reusable UI components
        - Services/API integration layers
        - Models/Data structures
        - Styling/Theme files
        - Configuration files
        - Assets and resources

        **3. Code Quality Standards:**
        - Clean, readable, well-documented code
        - Proper error handling and validation
        - Responsive design principles
        - Performance optimization
        - Security best practices
        - Accessibility considerations

        **4. Brand Integration:**
        - Integrate the provided brand palette into a centralized theme system
        - Ensure consistent styling across all components
        - Use appropriate colors for primary, secondary, text, and background elements

        **5. User Experience:**
        - Design intuitive navigation flow
        - Implement user-friendly interfaces based on the persona
        - Include loading states, error handling, and empty states
        - Ensure smooth user interactions

        **Output Format:**
        Generate each file as a separate code block with the file path as a comment header.
        Example:
        ```
        // File: lib/main.dart
        import 'package:flutter/material.dart';

        void main() {{
          runApp(MyApp());
        }}
        ```

        **Important Notes:**
        - Generate complete, functional code that can be compiled and run
        - Include all necessary imports and dependencies
        - Use modern best practices and current framework versions
        - Ensure the code is production-ready and maintainable
        - Focus on creating a polished, professional application
        """

        full_prompt = self._generate_prompt(task_description)

        try:
            # Use Anthropic API call through BaseAgent's model
            generated_code = self.generate_content(full_prompt)

            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.generated_code = generated_code
                project.status = Project.ProjectStatus.CODE_GENERATION_COMPLETE
                project.status_message = "Code generation complete. Production-ready mobile app generated."
                project.save()

            self.send_status_notification(project)

            print(f"Code generation complete for project {project_id}. Generated {len(generated_code)} characters of code.")

        except Exception as e:
            with transaction.atomic():
                project = Project.objects.select_for_update().get(id=project_id)
                project.status = Project.ProjectStatus.FAILED
                project.status_message = f"Code generation failed: {e}"
                project.save()
            print(f"Error during code generation for project {project_id}: {e}")
            raise
