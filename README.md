# NeuroEGE

AI-тренажёр ЕГЭ по информатике (Python-задачи).

## Требования

- Python 3.13+
- PostgreSQL 17+
- Django 6.0+
- **Linux / WSL Ubuntu** (sandbox требует `resource` модуль)
- uv (рекомендуется) или pip

> **Важно:** Sandbox для выполнения кода учеников использует `resource.setrlimit()`, который работает **только на Linux**. Для разработки на Windows используйте WSL.

## Разработка на Windows (WSL)

```powershell
# 1. Установить WSL Ubuntu
wsl --install -d Ubuntu-24.04

# 2. Войти в WSL
wsl
```

Далее все команды выполняются внутри WSL Ubuntu:

```bash
# 3. Установить зависимости системы
sudo apt update
sudo apt install python3.13 python3.13-venv postgresql

# 4. Склонировать проект (внутри WSL, НЕ на /mnt/c/)
cd ~
cp -r /mnt/c/W26/project/NeuroEGE ~/NeuroEGE
cd ~/NeuroEGE

# 5. Установить uv + зависимости
pip install uv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 6. PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE neuroege;"
sudo -u postgres psql -c "CREATE USER neuroege WITH PASSWORD 'password';"
sudo -u postgres psql -c "GRANT ALL ON DATABASE neuroege TO neuroege;"

# 7. Переменные окружения
cp .env.example .env
# nano .env  # отредактировать

# 8. Миграции
python manage.py migrate

# 9. Суперпользователь
python manage.py createsuperuser

# 10. Запуск
python manage.py runserver
# или ASGI:
uvicorn config.asgi:application --reload
```

### VS Code / Cursor + WSL

```powershell
# Открыть проект в WSL из Windows:
code --remote wsl+Ubuntu-24.04 ~/NeuroEGE
```

## Структура

```
NeuroEGE/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   └── dev.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── users/              # Кастомный User
│   ├── attempts/           # Попытки решений + AIAnalysis
│   ├── core/               # Базовые абстракции
│   ├── ai_engine/          # LLM клиент, prompts
│   ├── task_truth_table/   # №2 ЕГЭ
│   └── task_code_exec/     # №24-27 ЕГЭ (sandbox)
├── templates/
├── requirements.txt
├── manage.py
└── .env
```

## API

После запуска:

- `/admin/` — Django Admin
- `/api/v1/docs` — Swagger документация
- `/api/v1/users/me` — Текущий пользователь
- `/api/v1/attempts/` — Попытки
- `/api/v1/tasks/truth-table/` — Задания №2
- `/api/v1/tasks/code-exec/` — Задания №24-27

## Sandbox (выполнение кода)

Код учеников выполняется в изолированной среде с ограничениями:

| Лимит | Значение |
|-------|----------|
| CPU time | 5 сек |
| Memory | 256 MB |
| Processes | запрещено (no fork) |
| Imports | `os`, `subprocess` запрещены |

Реализация: `apps/task_code_exec/services.py`

## Технологии

- Django 6.0+ (async ORM, Tasks)
- Django Ninja (REST API)
- PostgreSQL 17+
- LangChain + DeepSeek/OpenAI
- HTMX (frontend, будет добавлен)
