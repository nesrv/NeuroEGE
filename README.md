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
# 3. Установить PostgreSQL
sudo apt update
sudo apt install postgresql

# 4. Установить uv (управляет Python + зависимостями)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # или перезапустить терминал

# 5. Склонировать проект (внутри WSL, НЕ на /mnt/c/)
cd ~
cp -r /mnt/c/W26/project/NeuroEGE ~/NeuroEGE
cd ~/NeuroEGE

# 6. Python 3.13 + venv + зависимости (uv сделает всё сам)
uv python install 3.13
uv venv --python 3.13
source .venv/bin/activate
uv pip install -r requirements.txt

# 7. Создать БД PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE neuroege;"
sudo -u postgres psql -c "CREATE USER neuroege WITH PASSWORD 'password';"
sudo -u postgres psql -c "GRANT ALL ON DATABASE neuroege TO neuroege;"

# 8. Переменные окружения
cp .env.example .env
# nano .env  # отредактировать

# 9. Миграции
python manage.py migrate

# 10. Суперпользователь
python manage.py createsuperuser

# 11. Запуск
python manage.py runserver
# или ASGI:
uvicorn config.asgi:application --reload
```

### VS Code / Cursor + WSL

```powershell
# Открыть проект в WSL из Windows:
code --remote wsl+Ubuntu-24.04 ~/NeuroEGE
```

### Синхронизация Windows → WSL

При редактировании в Windows (`c:\W26\project\NeuroEGE`) и запуске в WSL (`~/NeuroEGE`):

Создайте `~/NeuroEGE/sync-from-win.sh`:

```bash
#!/bin/bash
SRC="/mnt/c/W26/project/NeuroEGE"
DST="$HOME/NeuroEGE"
rsync -av --exclude '.venv' --exclude '__pycache__' --exclude '*.pyc' --exclude '.env' "$SRC/" "$DST/"
echo "Synced at $(date)"
```

```bash
# Первый раз: конвертировать line endings (CRLF → LF)
sed -i 's/\r$//' /mnt/c/W26/project/NeuroEGE/sync-from-win.sh

chmod +x ~/NeuroEGE/sync-from-win.sh
~/NeuroEGE/sync-from-win.sh   # или: bash /mnt/c/W26/project/NeuroEGE/sync-from-win.sh
```

**Из PowerShell (без входа в WSL):**

```powershell
wsl -e bash -c "sed -i 's/\r$//' /mnt/c/W26/project/NeuroEGE/sync-from-win.sh"
wsl -e bash -c "/mnt/c/W26/project/NeuroEGE/sync-from-win.sh"
```

### Ежедневная работа в WSL

```bash
cd ~/NeuroEGE

# 1. Синхронизировать изменения из Cursor (Windows)
./sync-from-win.sh

# 2. Активировать окружение
source .venv/bin/activate

# 3. При необходимости — обновить зависимости и миграции
uv pip install -r requirements.txt
python manage.py migrate

# 4. Запустить сервер
python manage.py runserver
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

### Аутентификация (JWT)

```bash
# Регистрация
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "student", "email": "student@test.ru", "password": "pass123"}'

# Ответ: {"access_token": "eyJ...", "token_type": "bearer"}

# Вход
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "student", "password": "pass123"}'

# Использование токена
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer eyJ..."
```

### Endpoints

| Endpoint | Auth | Описание |
|----------|------|----------|
| `POST /api/v1/users/register` | ❌ | Регистрация |
| `POST /api/v1/users/login` | ❌ | Вход |
| `GET /api/v1/users/me` | ✅ JWT | Текущий пользователь |
| `GET /api/v1/attempts/` | ✅ JWT | Попытки |
| `GET /api/v1/tasks/truth-table/` | ❌ | Задания №2 |
| `GET /api/v1/tasks/code-exec/` | ❌ | Задания №24-27 |

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
