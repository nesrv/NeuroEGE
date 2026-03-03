from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from ninja import Router, Schema

from .auth import JWTAuth, create_access_token

router = Router()
User = get_user_model()


class LoginSchema(Schema):
    username: str
    password: str


class RegisterSchema(Schema):
    username: str
    email: str
    password: str


class TokenSchema(Schema):
    access_token: str
    token_type: str = "bearer"


class UserSchema(Schema):
    id: int
    username: str
    email: str
    level_estimate: float
    target_score: int


class ErrorSchema(Schema):
    error: str


@router.post("/register", response={201: TokenSchema, 400: ErrorSchema})
async def register(request, data: RegisterSchema):
    """Регистрация нового пользователя."""
    if await User.objects.filter(username=data.username).aexists():
        return 400, {"error": "Username already exists"}

    if await User.objects.filter(email=data.email).aexists():
        return 400, {"error": "Email already exists"}

    user = await User.objects.acreate_user(
        username=data.username,
        email=data.email,
        password=data.password,
    )

    token = create_access_token(user.id)
    return 201, {"access_token": token, "token_type": "bearer"}


@router.post("/login", response={200: TokenSchema, 401: ErrorSchema})
async def login(request, data: LoginSchema):
    """Вход пользователя."""
    try:
        user = await User.objects.aget(username=data.username)
    except User.DoesNotExist:
        return 401, {"error": "Invalid credentials"}

    if not check_password(data.password, user.password):
        return 401, {"error": "Invalid credentials"}

    token = create_access_token(user.id)
    return 200, {"access_token": token, "token_type": "bearer"}


@router.get("/me", auth=JWTAuth(), response={200: UserSchema, 401: ErrorSchema})
async def get_current_user(request):
    """Получить текущего пользователя (требует JWT)."""
    user = request.auth
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "level_estimate": user.level_estimate,
        "target_score": user.target_score,
    }
