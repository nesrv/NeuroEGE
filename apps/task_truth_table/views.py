from ninja import Router, Schema

router = Router()


class SubmitAnswerSchema(Schema):
    task_id: int
    answer: str


@router.get("/")
async def list_tasks(request):
    """Список заданий на таблицы истинности."""
    from .models import TruthTableTask

    tasks = []
    async for task in TruthTableTask.objects.all()[:20]:
        tasks.append({
            "id": task.id,
            "number": task.number,
            "title": task.title,
            "difficulty": task.difficulty,
        })
    return {"tasks": tasks}


@router.get("/{task_id}")
async def get_task(request, task_id: int):
    """Получить задание по ID."""
    from .models import TruthTableTask

    try:
        task = await TruthTableTask.objects.aget(id=task_id)
        return {
            "id": task.id,
            "number": task.number,
            "title": task.title,
            "statement": task.statement,
            "expression": task.expression,
            "variables": task.variables,
            "difficulty": task.difficulty,
        }
    except TruthTableTask.DoesNotExist:
        return {"error": "Task not found"}


@router.post("/submit")
async def submit_answer(request, data: SubmitAnswerSchema):
    """Отправить ответ на задание."""
    from django.contrib.contenttypes.models import ContentType

    from apps.attempts.models import Attempt

    from .ai import analyze_truth_table_answer
    from .models import TruthTableTask

    user = await request.auser()
    if not user.is_authenticated:
        return {"error": "Not authenticated"}

    try:
        task = await TruthTableTask.objects.aget(id=data.task_id)
    except TruthTableTask.DoesNotExist:
        return {"error": "Task not found"}

    # AI анализ
    analysis = await analyze_truth_table_answer(
        expression=task.expression,
        user_answer=data.answer,
        correct_answer=task.correct_answer,
    )

    # Сохранение попытки
    content_type = await ContentType.objects.aget_for_model(TruthTableTask)
    attempt = await Attempt.objects.acreate(
        user=user,
        content_type=content_type,
        object_id=task.id,
        user_answer=data.answer,
        is_correct=analysis["is_correct"],
    )

    return {
        "attempt_id": attempt.id,
        "is_correct": analysis["is_correct"],
        "feedback": analysis["feedback"],
    }
