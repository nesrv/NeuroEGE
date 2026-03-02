from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

api = NinjaAPI(
    title="NeuroEGE API",
    version="1.0.0",
    description="AI-тренажёр ЕГЭ по информатике",
)

# Централизованная регистрация роутеров
from apps.users.views import router as users_router
from apps.attempts.views import router as attempts_router
from apps.task_truth_table.views import router as truth_table_router
from apps.task_code_exec.views import router as code_exec_router

api.add_router("/users", users_router, tags=["users"])
api.add_router("/attempts", attempts_router, tags=["attempts"])
api.add_router("/tasks/truth-table", truth_table_router, tags=["truth-table"])
api.add_router("/tasks/code-exec", code_exec_router, tags=["code-exec"])

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
]
