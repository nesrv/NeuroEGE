from ninja import Router

router = Router()


@router.get("/")
async def list_attempts(request):
    """Список попыток текущего пользователя."""
    from .models import Attempt

    user = await request.auser()
    if not user.is_authenticated:
        return {"error": "Not authenticated"}

    attempts = []
    async for attempt in Attempt.objects.filter(user=user).order_by("-created_at")[:20]:
        attempts.append({
            "id": attempt.id,
            "is_correct": attempt.is_correct,
            "created_at": attempt.created_at.isoformat(),
        })
    return {"attempts": attempts}


@router.get("/{attempt_id}")
async def get_attempt(request, attempt_id: int):
    """Получить попытку по ID."""
    from .models import Attempt

    try:
        attempt = await Attempt.objects.select_related("ai_analysis").aget(id=attempt_id)
        result = {
            "id": attempt.id,
            "user_code": attempt.user_code,
            "user_answer": attempt.user_answer,
            "is_correct": attempt.is_correct,
            "runtime": attempt.runtime,
            "created_at": attempt.created_at.isoformat(),
        }

        if hasattr(attempt, "ai_analysis"):
            result["ai_analysis"] = {
                "algorithm_type": attempt.ai_analysis.algorithm_type,
                "complexity": attempt.ai_analysis.complexity_estimate,
                "feedback": attempt.ai_analysis.feedback_text,
            }

        return result
    except Attempt.DoesNotExist:
        return {"error": "Attempt not found"}
