import anthropic
import os
from abc import ABC, abstractmethod
from apps.projects.tasks import send_project_status_notification

class BaseAgent(ABC):
    """
    Abstract Base Class for all AI Agents in the Applaude platform.
    """
    def __init__(self, agent_name: str, agent_persona: str, goal: str):
        """
        Initializes the agent with its core attributes.

        Args:
            agent_name (str): The name of the agent.
            agent_persona (str): A rich description of the agent's persona.
            goal (str): The primary objective of the agent.
        """
        self.agent_name = agent_name
        self.agent_persona = agent_persona
        self.goal = goal

        # Initialize Anthropic client
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"  # Claude Sonnet 4

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        The main method to run the agent's task. This must be implemented
        by all subclassed agents.
        """
        pass

    def _generate_prompt(self, task_description: str) -> str:
        """
        Constructs the final prompt to be sent to the Anthropic API.
        """
        return f"Persona: {self.agent_persona}\n\nGoal: {self.goal}\n\nTask: {task_description}"

    def generate_content(self, prompt: str) -> str:
        """
        Generates content using the Anthropic API.
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

    def send_status_notification(self, project, room_name='chat_room1'):
        """
        Sends WebSocket notification for project status update.
        """
        send_project_status_notification(project, room_name)

    def __repr__(self):
        return f"{self.agent_name}Agent"
