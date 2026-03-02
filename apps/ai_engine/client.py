import os
from typing import Any

import httpx


class LLMClient:
    """Async клиент для LLM API (DeepSeek, OpenAI-compatible)."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.deepseek.com/v1",
        model: str = "deepseek-chat",
    ):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = base_url
        self.model = model

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        """Отправить запрос к LLM."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            return response.json()

    async def analyze_code(
        self,
        code: str,
        task_statement: str,
        system_prompt: str | None = None,
    ) -> str:
        """Анализ кода с помощью LLM."""
        if system_prompt is None:
            system_prompt = (
                "Ты — эксперт ЕГЭ по информатике. "
                "Анализируй Python-код ученика, находи ошибки, "
                "объясняй доступно для 10-11 класса."
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Задача:\n{task_statement}\n\nКод ученика:\n```python\n{code}\n```",
            },
        ]

        result = await self.chat(messages)
        return result["choices"][0]["message"]["content"]


# Singleton instance
llm_client = LLMClient()
