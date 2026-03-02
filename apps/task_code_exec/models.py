from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from apps.attempts.models import Attempt
from apps.core.models import BaseTask, TimeStampedModel


class CodeExecTask(BaseTask, TimeStampedModel):
    """Задание на написание/анализ Python-кода (№24-27 ЕГЭ)."""

    input_description = models.TextField(
        help_text="Описание входных данных",
    )
    output_description = models.TextField(
        help_text="Описание выходных данных",
    )
    test_cases = models.JSONField(
        default=list,
        help_text="Тестовые случаи: [{'input': '...', 'output': '...'}]",
    )
    official_solution = models.TextField(
        blank=True,
        help_text="Официальное решение",
    )
    time_limit = models.FloatField(
        default=5.0,
        help_text="Лимит времени (сек)",
    )
    memory_limit = models.IntegerField(
        default=256,
        help_text="Лимит памяти (MB)",
    )

    attempts = GenericRelation(Attempt)

    class Meta:
        verbose_name = "Задание: Python-код"
        verbose_name_plural = "Задания: Python-код"
