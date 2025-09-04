import google.generativeai as genai
import os
from abc import ABC, abstractmethod

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
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        The main method to run the agent's task. This must be implemented
        by all subclassed agents.
        """
        pass

    def _generate_prompt(self, task_description: str) -> str:
        """
        Constructs the final prompt to be sent to the Gemini API.
        """
        return f"Persona: {self.agent_persona}\n\nGoal: {self.goal}\n\nTask: {task_description}"

    def __repr__(self):
        return f"{self.agent_name}Agent"
