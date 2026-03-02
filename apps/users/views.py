from ninja import Router

router = Router()


@router.get("/me")
async def get_current_user(request):
    """Получить текущего пользователя."""
    user = await request.auser()
    if user.is_authenticated:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "level_estimate": user.level_estimate,
            "target_score": user.target_score,
        }
    return {"error": "Not authenticated"}
