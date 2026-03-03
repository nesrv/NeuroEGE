"""Бизнес-логика для заданий на таблицы истинности.

Этот модуль НЕ импортирует Django ORM.
Чистые функции для логических вычислений.
"""


def parse_expression(expression: str) -> str:
    """Преобразовать логическое выражение в Python-синтаксис."""
    replacements = {
        "∧": " and ",
        "∨": " or ",
        "¬": " not ",
        "→": " <= ",  # импликация: A → B = ¬A ∨ B
        "↔": " == ",  # эквиваленция
        "⊕": " ^ ",   # XOR
    }
    result = expression
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result


def evaluate_expression(expression: str, values: dict[str, bool]) -> bool:
    """Вычислить значение логического выражения."""
    python_expr = parse_expression(expression)
    return eval(python_expr, {"__builtins__": {}}, values)


def generate_truth_table(
    expression: str,
    variables: list[str],
) -> list[dict]:
    """Сгенерировать таблицу истинности."""
    n = len(variables)
    table = []

    for i in range(2**n):
        values = {}
        for j, var in enumerate(variables):
            values[var] = bool((i >> (n - 1 - j)) & 1)

        result = evaluate_expression(expression, values)
        table.append({**values, "result": result})

    return table


def check_answer(user_answer: str, correct_answer: str) -> bool:
    """Проверить ответ пользователя."""
    return user_answer.strip().lower() == correct_answer.strip().lower()
