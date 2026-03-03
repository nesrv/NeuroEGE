"""Views для главной страницы и общих UI-компонентов."""

from django.shortcuts import render


def home(request):
    """Главная страница NeuroEGE."""
    # Задания 1–27: данные об иконках Python/Excel/Word/Brain
    PYTHON_TASKS = {2, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 23, 24, 25, 26, 27}
    EXCEL_TASKS = {3, 9, 12, 18, 22, 26}
    WORD_TASKS = {10}
    BRAIN_TASKS = {1, 2, 4, 7, 11, 12, 15, 19, 20, 21}

    tasks = [
        {
            "number": n,
            "has_python": n in PYTHON_TASKS,
            "has_excel": n in EXCEL_TASKS,
            "has_word": n in WORD_TASKS,
            "has_brain": n in BRAIN_TASKS,
        }
        for n in range(1, 28)
    ]

    return render(request, "core/home.html", {"tasks": tasks})
