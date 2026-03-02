from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя для NeuroEGE."""

    level_estimate = models.FloatField(
        default=0.5,
        help_text="Оценка уровня подготовки (0-1)",
    )
    stress_level = models.FloatField(
        default=0.3,
        help_text="Уровень стресса (0-1)",
    )
    target_score = models.IntegerField(
        default=80,
        help_text="Целевой балл ЕГЭ",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
