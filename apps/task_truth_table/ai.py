"""AI prompts и chains для заданий на таблицы истинности."""

from apps.ai_engine.client import llm_client
from apps.ai_engine.prompts import SYSTEM_EXPERT


TRUTH_TABLE_SYSTEM = f"""{SYSTEM_EXPERT}

Специализация: задания на таблицы истинности (№2 ЕГЭ).
Объясняй логические операции, законы де Моргана, приоритет операций."""


async def analyze_truth_table_answer(
    expression: str,
    user_answer: str,
    correct_answer: str,
) -> dict:
    """Анализ ответа на задание по таблицам истинности."""
    is_correct = user_answer.strip() == correct_answer.strip()

    if is_correct:
        feedback = "Правильно! Ты верно построил таблицу истинности."
    else:
        response = await llm_client.chat(
            messages=[
                {"role": "system", "content": TRUTH_TABLE_SYSTEM},
                {
                    "role": "user",
                    "content": f"""Выражение: {expression}
Ответ ученика: {user_answer}
Правильный ответ: {correct_answer}

Объясни ошибку кратко и понятно.""",
                },
            ],
            temperature=0.5,
            max_tokens=500,
        )
        feedback = response["choices"][0]["message"]["content"]

    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "confidence": 0.95 if is_correct else 0.8,
    }
