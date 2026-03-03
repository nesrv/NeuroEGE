from django.db import models


class TimeStampedModel(models.Model):
    """Базовая модель с временными метками."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseTask(models.Model):
    """Базовая абстракция для всех типов заданий ЕГЭ."""

    number = models.IntegerField(help_text="Номер задания ЕГЭ (2, 5, 12, 24-27)")
    title = models.CharField(max_length=255)
    statement = models.TextField(help_text="Условие задачи")
    difficulty = models.IntegerField(default=5, help_text="Сложность (1-10)")
    concepts = models.JSONField(default=list, help_text="Связанные концепции")

    class Meta:
        abstract = True

    def __str__(self):
        return f"№{self.number}: {self.title}"
