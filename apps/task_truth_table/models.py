from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from apps.attempts.models import Attempt
from apps.core.models import BaseTask, TimeStampedModel


class TruthTableTask(BaseTask, TimeStampedModel):
    """Задание на таблицы истинности (№2 ЕГЭ)."""

    expression = models.CharField(
        max_length=255,
        help_text="Логическое выражение, например: (A ∨ B) ∧ ¬C",
    )
    variables = models.JSONField(
        default=list,
        help_text="Список переменных: ['A', 'B', 'C']",
    )
    correct_answer = models.TextField(
        help_text="Правильный ответ",
    )

    attempts = GenericRelation(Attempt)

    class Meta:
        verbose_name = "Задание: Таблица истинности"
        verbose_name_plural = "Задания: Таблицы истинности"
