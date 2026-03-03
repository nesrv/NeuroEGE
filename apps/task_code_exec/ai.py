"""AI prompts и chains для заданий с Python-кодом."""

import json

from apps.ai_engine.client import llm_client
from apps.ai_engine.prompts import ANALYZE_CODE_PROMPT, SYSTEM_EXPERT


CODE_EXEC_SYSTEM = f"""{SYSTEM_EXPERT}

Специализация: задания на Python-код (№24-27 ЕГЭ).
Анализируй алгоритмы, находи логические ошибки, оценивай сложность.
Отвечай в формате JSON когда это указано."""


async def analyze_user_code(
    task_statement: str,
    user_code: str,
    test_results: dict | None = None,
) -> dict:
    """Глубокий AI-анализ кода ученика."""
    context = f"Задача:\n{task_statement}\n\nКод ученика:\n```python\n{user_code}\n```"

    if test_results:
        context += f"\n\nРезультаты тестов: {test_results['passed']}/{test_results['total']} пройдено"
        if not test_results["all_passed"]:
            failed = [r for r in test_results["results"] if not r["passed"]]
            if failed:
                context += f"\nПервый провал: ожидалось '{failed[0]['expected']}', получено '{failed[0]['actual']}'"

    prompt = ANALYZE_CODE_PROMPT.format(
        task_statement=task_statement,
        user_code=user_code,
    )

    response = await llm_client.chat(
        messages=[
            {"role": "system", "content": CODE_EXEC_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=1000,
    )

    content = response["choices"][0]["message"]["content"]

    # Попытка распарсить JSON
    try:
        # Ищем JSON в ответе
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(content[start:end])
    except json.JSONDecodeError:
        pass

    # Fallback если JSON не распарсился
    return {
        "algorithm_type": "unknown",
        "mistakes": [],
        "complexity": "unknown",
        "feedback": content,
        "better_idea": "",
        "confidence": 0.5,
    }


async def get_hint(
    task_statement: str,
    user_code: str,
    level: int = 1,
) -> str:
    """Получить подсказку определённого уровня."""
    from apps.ai_engine.prompts import HINT_LEVELS

    hint_instruction = HINT_LEVELS.get(level, HINT_LEVELS[1])

    response = await llm_client.chat(
        messages=[
            {"role": "system", "content": CODE_EXEC_SYSTEM},
            {
                "role": "user",
                "content": f"""Задача: {task_statement}

Текущий код ученика:
```python
{user_code}
```

{hint_instruction}""",
            },
        ],
        temperature=0.5,
        max_tokens=500,
    )

    return response["choices"][0]["message"]["content"]
