from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.core.models import TimeStampedModel


class Attempt(TimeStampedModel):
    """Универсальная попытка решения (связь с любым типом задания)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attempts",
    )

    # Generic relation к любому типу задания
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    task = GenericForeignKey("content_type", "object_id")

    user_code = models.TextField(blank=True, help_text="Код пользователя")
    user_answer = models.TextField(blank=True, help_text="Ответ пользователя")

    is_correct = models.BooleanField(null=True, help_text="Правильность решения")
    runtime = models.FloatField(null=True, help_text="Время выполнения (сек)")
    memory = models.FloatField(null=True, help_text="Использованная память (MB)")

    class Meta:
        verbose_name = "Попытка"
        verbose_name_plural = "Попытки"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "content_type", "object_id"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"Attempt #{self.id} by {self.user}"


class AIAnalysis(TimeStampedModel):
    """AI-анализ попытки решения."""

    attempt = models.OneToOneField(
        Attempt,
        on_delete=models.CASCADE,
        related_name="ai_analysis",
    )

    algorithm_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Тип алгоритма: bruteforce, optimized, math, dp",
    )
    complexity_estimate = models.CharField(
        max_length=20,
        blank=True,
        help_text="Оценка сложности: O(n), O(n^2), etc.",
    )
    logic_errors = models.JSONField(
        default=list,
        help_text="Список логических ошибок",
    )
    feedback_text = models.TextField(
        blank=True,
        help_text="Текстовый фидбэк от AI",
    )
    suggested_approach = models.TextField(
        blank=True,
        help_text="Предложенный подход к решению",
    )
    confidence_score = models.FloatField(
        default=0.0,
        help_text="Уверенность AI в анализе (0-1)",
    )

    class Meta:
        verbose_name = "AI-анализ"
        verbose_name_plural = "AI-анализы"

    def __str__(self):
        return f"Analysis for {self.attempt}"
