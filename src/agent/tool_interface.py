from typing import Tuple
from groq import Groq
from src.executor.sandbox_executor import SandboxExecutor

class LLMInterface:
    """
    Abstracción para interactuar con Groq Cloud.
    """
    def __init__(self, api_key: str, model: str):
        self.client = Groq(api_key=api_key)
        self.model = model

    def complete(self, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Eres un agente que genera código Python con pandas."},
                {"role": "user",   "content": prompt}
            ],
            stream=False
        )
        return resp.choices[0].message.content.strip() # type: ignore

class SandboxInterface:
    """
    Abstracción para ejecución en sandbox.
    """
    def __init__(self, cpu_time: int, memory_bytes: int, user_name: str):
        self.executor = SandboxExecutor(cpu_time=cpu_time, memory_bytes=memory_bytes, user_name=user_name)

    def run(self, code: str, timeout: int = 5) -> Tuple[str, str]:
        return self.executor.execute_code(code, timeout=timeout)
