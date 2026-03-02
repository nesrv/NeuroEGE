from ninja import Router, Schema

router = Router()


class SubmitCodeSchema(Schema):
    task_id: int
    code: str


class HintRequestSchema(Schema):
    task_id: int
    code: str = ""
    level: int = 1


@router.get("/")
async def list_tasks(request):
    """Список заданий на Python-код."""
    from .models import CodeExecTask

    tasks = []
    async for task in CodeExecTask.objects.all()[:20]:
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
    from .models import CodeExecTask

    try:
        task = await CodeExecTask.objects.aget(id=task_id)
        return {
            "id": task.id,
            "number": task.number,
            "title": task.title,
            "statement": task.statement,
            "input_description": task.input_description,
            "output_description": task.output_description,
            "difficulty": task.difficulty,
            "time_limit": task.time_limit,
        }
    except CodeExecTask.DoesNotExist:
        return {"error": "Task not found"}


@router.post("/submit")
async def submit_code(request, data: SubmitCodeSchema):
    """Отправить код на проверку."""
    from django.contrib.contenttypes.models import ContentType

    from apps.attempts.models import AIAnalysis, Attempt

    from .ai import analyze_user_code
    from .models import CodeExecTask
    from .services import run_tests

    user = await request.auser()
    if not user.is_authenticated:
        return {"error": "Not authenticated"}

    try:
        task = await CodeExecTask.objects.aget(id=data.task_id)
    except CodeExecTask.DoesNotExist:
        return {"error": "Task not found"}

    # Выполнение тестов
    test_results = run_tests(
        code=data.code,
        test_cases=task.test_cases,
        timeout=int(task.time_limit),
    )

    # AI анализ
    ai_result = await analyze_user_code(
        task_statement=task.statement,
        user_code=data.code,
        test_results=test_results,
    )

    # Сохранение попытки
    content_type = await ContentType.objects.aget_for_model(CodeExecTask)
    attempt = await Attempt.objects.acreate(
        user=user,
        content_type=content_type,
        object_id=task.id,
        user_code=data.code,
        is_correct=test_results["all_passed"],
        runtime=max(r["runtime"] for r in test_results["results"]) if test_results["results"] else 0,
    )

    # Сохранение AI-анализа
    await AIAnalysis.objects.acreate(
        attempt=attempt,
        algorithm_type=ai_result.get("algorithm_type", ""),
        complexity_estimate=ai_result.get("complexity", ""),
        logic_errors=ai_result.get("mistakes", []),
        feedback_text=ai_result.get("feedback", ""),
        suggested_approach=ai_result.get("better_idea", ""),
        confidence_score=ai_result.get("confidence", 0),
    )

    return {
        "attempt_id": attempt.id,
        "is_correct": test_results["all_passed"],
        "tests": test_results,
        "ai_analysis": ai_result,
    }


@router.post("/hint")
async def get_hint(request, data: HintRequestSchema):
    """Получить подсказку."""
    from .ai import get_hint as ai_get_hint
    from .models import CodeExecTask

    try:
        task = await CodeExecTask.objects.aget(id=data.task_id)
    except CodeExecTask.DoesNotExist:
        return {"error": "Task not found"}

    hint = await ai_get_hint(
        task_statement=task.statement,
        user_code=data.code,
        level=data.level,
    )

    return {"level": data.level, "hint": hint}
