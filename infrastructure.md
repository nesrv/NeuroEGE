# Расчёт метрик, нагрузки и инфраструктуры NeuroEGE

## Технологии 2026-27 Edition

> Максимально экономичная архитектура с использованием Django 6+, PostgreSQL 18+, serverless и современных LLM API.

---

## Исходные данные

| Параметр | Год 1 | Год 2 |
|----------|-------|-------|
| Пользователей | 5,000 | 20,000 |
| % рынка ЕГЭ (150k/год) | 3.3% | 13.3% |

---

## 1. Поведенческие метрики (прогноз)

| Метрика | Оценка |
|---------|--------|
| Сессий в неделю на юзера | 3-4 |
| Среднее время сессии | 25-40 мин |
| Попыток (attempts) за сессию | 5-8 |
| AI-запросов за сессию | 8-12 (анализ + подсказки + генерация) |
| Пик активности | 18:00-22:00 (вечер), воскресенье |
| Сезонность | x3-5 в апреле-июне (перед ЕГЭ) |

---

## 2. Расчёт нагрузки

### Год 1 (5,000 пользователей)

```
DAU (daily active users):
- обычный день: ~15% = 750 чел
- пик (апрель-июнь): ~40% = 2,000 чел

Сессий в день (пик): 2,000 × 1.5 = 3,000 сессий
Попыток в день: 3,000 × 6 = 18,000 attempts
AI-запросов в день: 3,000 × 10 = 30,000 LLM calls

RPS (requests per second):
- Пиковые 4 часа = 14,400 сек
- HTTP requests: ~100,000 / 14,400 ≈ 7 RPS
- AI requests: 30,000 / 14,400 ≈ 2 RPS
```

### Год 2 (20,000 пользователей)

```
DAU (пик): 8,000 чел
Сессий в день (пик): 12,000
Попыток в день: 72,000 attempts  
AI-запросов в день: 120,000 LLM calls

RPS (пик):
- HTTP: ~28 RPS
- AI: ~8 RPS
- Code execution: ~5 RPS
```

---

## 3. Ключевые технологии 2026-27

### Django 6.0+ (декабрь 2025)

| Фича | Экономия | Как использовать |
|------|----------|------------------|
| **Native Async ORM** | -30% latency | Async views + async ORM без `sync_to_async` |
| **Built-in Tasks Framework** | **Убираем Celery!** | Background jobs через встроенный механизм |
| **Full Async Stack** | -1 worker | Меньше воркеров для той же нагрузки |
| **Template Partials** | Быстрее рендер | Переиспользование компонентов |

```python
# Django 6.0 — нативный async без обёрток
async def analyze_solution(request):
    attempt = await Attempt.objects.aget(id=attempt_id)  # Native async!
    analysis = await llm_analyze(attempt.user_code)      # Concurrent I/O
    await AIAnalysis.objects.acreate(attempt=attempt, **analysis)
    return JsonResponse(analysis)

# Встроенные Tasks — прощай Celery!
from django.tasks import task

@task
async def process_code_async(attempt_id: int):
    # Выполняется в фоне через DB-backed queue
    ...
```

### PostgreSQL 18+ (сентябрь 2025)

| Фича | Экономия | Применение |
|------|----------|------------|
| **AIO Subsystem (io_uring)** | +50% I/O | Быстрые SELECT/INSERT на attempts |
| **Skip Scan** | +30% index queries | Multicolumn индексы (user_id, task_id) |
| **UUIDv7** | Быстрее вставки | Timestamp-ordered IDs |
| **Virtual Generated Columns** | -20% storage | Вычисляемые поля без хранения |
| **Optimized JSON** | Быстрее анализ | AIAnalysis.feedback_json |

```sql
-- PostgreSQL 18 конфигурация для максимальной производительности
SET io_method = 'io_uring';      -- Асинхронный I/O
SET io_workers = 4;               -- Worker-ы для I/O
SET io_max_concurrency = 32;      -- Параллельные операции

-- Virtual generated columns — не занимают место
ALTER TABLE attempts ADD COLUMN 
    complexity_class VARCHAR(20) 
    GENERATED ALWAYS AS (
        CASE 
            WHEN runtime < 0.1 THEN 'fast'
            WHEN runtime < 1.0 THEN 'normal'
            ELSE 'slow'
        END
    ) VIRTUAL;
```

---

## 4. База данных — PostgreSQL 18 на VPS

### Почему локальный PostgreSQL (а не Neon/облако)

У вас есть VPS с 60 GB NVMe — облачная БД не нужна:

| Вариант | Стоимость | Latency | Для вас |
|---------|-----------|---------|---------|
| Neon serverless | $30-220/мес | 20-50ms | ❌ лишние затраты |
| **PostgreSQL 18 локально** | **$0** | **<1ms** | ✅ оптимально |

### Sizing (помещается на 60 GB)

| Таблица | Год 1 | Год 2 |
|---------|-------|-------|
| Users | 2.5 MB | 10 MB |
| Tasks | 200 KB | 500 KB |
| Attempts | 1.5 GB | 6 GB |
| AIAnalysis | 3 GB | 12 GB |
| SkillProfile | 10 MB | 40 MB |
| **Итого** | **~5 GB** | **~20 GB** |

**Вывод:** 60 GB NVMe хватит на 3+ года.

### Конфигурация PostgreSQL 18 для 4 GB RAM

```ini
# /etc/postgresql/18/main/conf.d/neuroege.conf

# Память (консервативно)
shared_buffers = 512MB
effective_cache_size = 1GB
work_mem = 32MB
maintenance_work_mem = 128MB

# I/O — главная фича PostgreSQL 18!
io_method = 'io_uring'
io_workers = 2
io_max_concurrency = 16

# Connections
max_connections = 50
```

### Индексы для производительности

```sql
CREATE INDEX idx_attempts_user_task ON attempts(user_id, task_id);
CREATE INDEX idx_attempts_created ON attempts(created_at DESC);
CREATE INDEX idx_aianalysis_attempt ON aianalysis(attempt_id);
```

---

## 5. Серверная инфраструктура 2026

### Ваш VPS (Hostiman RVDS3)

```
┌─────────────────────────────────────────────────────────┐
│                  Hostiman RVDS3                         │
│  CPU: 3x3700 MHz    RAM: 4 GB    NVMe: 60 GB            │
│  Backup: 120 GB HDD    Port: 100 Mbit                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │ Caddy   │→ │ Django 6.0   │→ │ PostgreSQL 18       │ │
│  │ (proxy) │  │ + Uvicorn    │  │ (local, io_uring)   │ │
│  │ + SSL   │  │ 2 workers    │  │                     │ │
│  └─────────┘  └──────────────┘  └─────────────────────┘ │
│                      ↓                                  │
│              ┌───────────────┐                          │
│              │ Code Sandbox  │ (subprocess + rlimit)    │
│              │ (no Docker!)  │                          │
│              └───────────────┘                          │
└─────────────────────────────────────────────────────────┘
                       ↓
              ┌───────────────┐
              │   LLM API     │ DeepSeek / Gemini / Qwen3
              └───────────────┘
```

### Характеристики и лимиты

| Ресурс | Есть | Нужно (Год 1) | Нужно (Год 2) | Статус |
|--------|------|---------------|---------------|--------|
| CPU | 3 ядра | 2-3 ядра | 4+ ядер | ✅ OK → ⚠️ апгрейд |
| RAM | 4 GB | 2-3 GB | 6-8 GB | ✅ OK → ⚠️ апгрейд |
| Disk | 60 GB | 10 GB | 30 GB | ✅ OK |
| Network | 100 Mbit | 50 Mbit | 100 Mbit | ✅ OK |

**Вывод:** VPS хватит на Год 1 (5k users). Для Года 2 — апгрейд до RVDS4 или добавить второй сервер.

### Оптимизация под 4 GB RAM

```bash
# PostgreSQL 18 — минимальная память
shared_buffers = 512MB
effective_cache_size = 1GB
work_mem = 32MB
maintenance_work_mem = 128MB

# Uvicorn — 2 workers (экономия RAM)
uvicorn config.asgi:application --workers 2 --host 0.0.0.0 --port 8000

# Распределение памяти:
# - PostgreSQL: ~1 GB
# - Django/Uvicorn: ~1 GB  
# - System + sandbox: ~1.5 GB
# - Резерв: ~0.5 GB
```

### Sandbox без Docker (экономия 1+ GB RAM)

С 4 GB RAM Docker-контейнеры — роскошь. Используем **subprocess + rlimit**:

```python
# sandbox/runner.py — легковесный sandbox
import subprocess
import resource
import os

def run_user_code(code: str, stdin: str, timeout: int = 5) -> dict:
    """Запуск кода без Docker — экономия RAM"""
    
    def set_limits():
        # Ограничения для дочернего процесса
        resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))      # CPU time
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2) # 256 MB RAM
        resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024,) * 2)    # 1 MB файлы
        resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))                # Нет fork
    
    # Запрещённые импорты проверяем ДО запуска
    forbidden = ['os.system', 'subprocess', 'eval(', 'exec(', '__import__']
    if any(f in code for f in forbidden):
        return {"error": "Запрещённый код", "stdout": "", "stderr": ""}
    
    try:
        result = subprocess.run(
            ["python3", "-c", code],
            input=stdin,
            capture_output=True,
            timeout=timeout,
            text=True,
            preexec_fn=set_limits,
            env={"PATH": "/usr/bin"}  # Минимальный PATH
        )
        return {
            "stdout": result.stdout[:10000],
            "stderr": result.stderr[:10000],
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": "Timeout", "stdout": "", "stderr": "Превышено время"}
    except Exception as e:
        return {"error": str(e), "stdout": "", "stderr": ""}
```

### Альтернатива: Modal для sandbox (если нужна изоляция)

Если subprocess недостаточно безопасен — выносим sandbox в Modal:

Вместо своих Docker-контейнеров → **Modal** (serverless compute):

```python
import modal

app = modal.App("neuroege-sandbox")

@app.function(
    timeout=5,
    memory=256,
    cpu=0.5,
)
def run_user_code(code: str, stdin: str) -> dict:
    # Изолированное выполнение, платишь за мс
    import subprocess
    result = subprocess.run(
        ["python", "-c", code],
        input=stdin,
        capture_output=True,
        timeout=5
    )
    return {
        "stdout": result.stdout.decode(),
        "stderr": result.stderr.decode(),
        "returncode": result.returncode
    }
```

**Pricing Modal:**
- $0.000016/секунда CPU
- 30,000 executions × 3 сек = $1.44/мес (!!!)

---

## 6. LLM API 2026 — Революция цен

### Актуальные цены (февраль 2026)

| Модель | Input $/1M | Output $/1M | Качество | Рекомендация |
|--------|------------|-------------|----------|--------------|
| **Qwen3 235B** | $0.00 | $0.00 | ★★★★☆ | Бесплатно! OpenRouter |
| **DeepSeek V3** | $0.14 | $0.28 | ★★★★☆ | **Best value** |
| **Gemini 2.5 Flash-Lite** | $0.10 | $0.40 | ★★★★☆ | Очень дёшево |
| **GPT-5 Nano** | $0.05 | $0.40 | ★★★☆☆ | Baseline |
| **GPT-5 Mini** | $0.25 | $2.00 | ★★★★☆ | Средний |
| **Claude Haiku 4.5** | $1.00 | $5.00 | ★★★★★ | Премиум |

### Расчёт для NeuroEGE

**Средний запрос:** 1,200 input + 700 output = 1,900 токенов

**Год 1 (30,000 запросов/день в пик):**

| Стратегия | Модель | Стоимость/мес |
|-----------|--------|---------------|
| **Ultra-budget** | Qwen3 (free) | $0 |
| **Budget** | DeepSeek V3 | ~$12/мес (~1,200 ₽) |
| **Balanced** | Gemini Flash-Lite | ~$15/мес (~1,500 ₽) |
| **Premium** | GPT-5 Mini | ~$70/мес (~7,000 ₽) |

**Рекомендация:** DeepSeek V3 или Gemini Flash — **в 50 раз дешевле** GPT-4o образца 2024!

### Tiered Strategy 2026

```python
# Уровневая система — максимальная экономия
async def get_ai_response(task: str, complexity: str) -> dict:
    match complexity:
        case "simple":
            # Простые подсказки — бесплатная модель
            return await call_qwen3(task)
        
        case "medium":
            # Анализ кода — дешёвая модель
            return await call_deepseek_v3(task)
        
        case "complex":
            # Глубокий разбор — средняя модель
            return await call_gemini_flash(task)
        
        case "expert":
            # Сложные случаи — премиум
            return await call_gpt5_mini(task)
```

---

## 7. Финансовая сводка 2026 (С ВАШИМ VPS)

### Год 1 (5,000 пользователей)

| Статья | Было бы (без VPS) | **С вашим VPS** | Примечание |
|--------|-------------------|-----------------|------------|
| VPS Hostiman RVDS3 | — | **уже есть** | ~500-1000 ₽/мес |
| БД PostgreSQL | 3,000 ₽ | **0 ₽** | Локально на VPS |
| Sandbox | 2,000 ₽ | **0 ₽** | subprocess, не Docker |
| LLM API (DeepSeek) | 4,000-60,000 ₽ | **500-3,000 ₽** | 30k req/день |
| CDN (Cloudflare) | 2,000 ₽ | **0 ₽** | Free plan |
| Домен + SSL | 1,500 ₽ | **150 ₽** | Caddy + Let's Encrypt |
| **Итого/мес** | 8,000-70,000 ₽ | **500-3,500 ₽** | **-95%** |

### Год 2 (20,000 пользователей)

| Статья | Стоимость | Примечание |
|--------|-----------|------------|
| VPS Hostiman RVDS4/5 | **1,500-2,500 ₽** | Апгрейд до 8 GB RAM |
| БД PostgreSQL | **0 ₽** | Всё ещё локально |
| Sandbox (Modal fallback) | **500-1,500 ₽** | Только для тяжёлых случаев |
| LLM API | **2,000-10,000 ₽** | Tiered: Qwen→DeepSeek→Gemini |
| CDN (Cloudflare) | **0 ₽** | Free plan хватит |
| Бэкапы (Cloudflare R2) | **100-300 ₽** | ~10 GB |
| **Итого/мес** | **4,000-15,000 ₽** | **-90% vs классика** |

### Сравнение затрат

```
               Год 1                    Год 2
         ┌─────────────────┐     ┌─────────────────┐
Классика │  8-70k ₽/мес    │     │ 50-300k ₽/мес   │
         └─────────────────┘     └─────────────────┘
                ↓ -95%                  ↓ -90%
         ┌─────────────────┐     ┌─────────────────┐
Ваш VPS  │  0.5-3.5k ₽/мес │     │  4-15k ₽/мес    │
         └─────────────────┘     └─────────────────┘
```

---

## 8. Архитектура Django 6.0

### Прощай Celery, привет Django Tasks!

```python
# settings.py — Django 6.0 Tasks
TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.database.DatabaseBackend",
        "QUEUES": ["default", "ai", "sandbox"],
    }
}

# tasks.py
from django.tasks import task, shared_task

@task(queue="ai")
async def analyze_attempt_async(attempt_id: int):
    attempt = await Attempt.objects.select_related("task").aget(id=attempt_id)
    
    # Async LLM call
    analysis = await deepseek_analyze(
        code=attempt.user_code,
        task=attempt.task.statement
    )
    
    await AIAnalysis.objects.acreate(
        attempt=attempt,
        **analysis
    )

@task(queue="sandbox")
async def execute_code_async(attempt_id: int):
    # Modal serverless execution
    result = await modal_run_code(attempt.user_code)
    await Attempt.objects.filter(id=attempt_id).aupdate(
        runtime=result["runtime"],
        is_correct=result["correct"]
    )
```

### Full Async View

```python
# views.py — Django 6.0 полностью async
from django.http import JsonResponse
from ninja import Router

router = Router()

@router.post("/attempt/")
async def submit_attempt(request, data: AttemptSchema):
    # Всё async — никаких sync_to_async!
    user = await request.auser()
    task = await Task.objects.aget(id=data.task_id)
    
    attempt = await Attempt.objects.acreate(
        user=user,
        task=task,
        user_code=data.code
    )
    
    # Запускаем фоновые задачи (Django Tasks, не Celery!)
    await execute_code_async.aenqueue(attempt.id)
    await analyze_attempt_async.aenqueue(attempt.id)
    
    return {"attempt_id": attempt.id, "status": "processing"}
```

---

## 9. Локальная разработка (Windows)

### Установка PostgreSQL на Windows

```powershell
# Вариант 1: winget (рекомендую)
winget install PostgreSQL.PostgreSQL

# Вариант 2: Scoop
scoop install postgresql

# Вариант 3: Официальный установщик
# https://www.postgresql.org/download/windows/
```

После установки PostgreSQL работает как Windows Service (автозапуск).

### Создание БД для разработки

```powershell
# Открыть PowerShell и выполнить:
psql -U postgres

# В psql:
CREATE DATABASE neuroege;
CREATE USER neuroege WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE neuroege TO neuroege;
ALTER DATABASE neuroege OWNER TO neuroege;
\q
```

### Переменные окружения (.env)

```ini
# .env (локальная разработка)
DATABASE_URL=postgres://neuroege:dev_password@localhost:5432/neuroege
DEEPSEEK_API_KEY=sk-xxx
SECRET_KEY=dev-secret-key-change-in-prod
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Запуск проекта

```powershell
# 1. Клонируем
git clone https://github.com/your/neuroege.git
cd neuroege

# 2. Виртуальное окружение (Python 3.12+)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Зависимости
pip install -r requirements.txt

# 4. Миграции
python manage.py migrate

# 5. Запуск dev-сервера
python manage.py runserver

# Или с ASGI (ближе к проду):
uvicorn config.asgi:application --reload
```

### Версии PostgreSQL: dev vs prod

| Среда | PostgreSQL | Особенности |
|-------|------------|-------------|
| Windows (dev) | 16/17 | Стабильные, без io_uring |
| Ubuntu (prod) | **18** | io_uring (+50% I/O) |

Разница для Django несущественна — миграции совместимы. На проде просто быстрее.

### pgAdmin (GUI для Windows)

```powershell
# Устанавливается вместе с PostgreSQL или отдельно:
winget install PostgreSQL.pgAdmin
```

Удобно для просмотра данных, отладки запросов.

---

## 10. Deployment на VPS (Ubuntu)

### Быстрый старт

```bash
# 1. Подключаемся к VPS
ssh root@your-vps-ip

# 2. Устанавливаем зависимости (Ubuntu 24.04+)
apt update && apt upgrade -y
apt install -y python3.13 python3.13-venv postgresql-18 caddy

# 3. Настраиваем PostgreSQL 18 с io_uring
sudo -u postgres psql -c "CREATE DATABASE neuroege;"
sudo -u postgres psql -c "CREATE USER neuroege WITH PASSWORD 'secure_pass';"
sudo -u postgres psql -c "GRANT ALL ON DATABASE neuroege TO neuroege;"

# postgresql.conf оптимизация для 4 GB RAM
echo "shared_buffers = 512MB
effective_cache_size = 1GB
work_mem = 32MB
io_method = 'io_uring'" >> /etc/postgresql/18/main/conf.d/neuroege.conf

systemctl restart postgresql

# 4. Клонируем проект
cd /opt
git clone https://github.com/your/neuroege.git
cd neuroege

# 5. Виртуальное окружение
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 6. Переменные окружения
cat > .env << 'EOF'
DATABASE_URL=postgres://neuroege:secure_pass@localhost/neuroege
DEEPSEEK_API_KEY=sk-xxx
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.ru
EOF

# 7. Миграции
python manage.py migrate
python manage.py collectstatic --noinput

# 8. Systemd сервис
cat > /etc/systemd/system/neuroege.service << 'EOF'
[Unit]
Description=NeuroEGE Django ASGI
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/neuroege
Environment="PATH=/opt/neuroege/.venv/bin"
EnvironmentFile=/opt/neuroege/.env
ExecStart=/opt/neuroege/.venv/bin/uvicorn config.asgi:application \
    --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable neuroege
systemctl start neuroege

# 9. Caddy (reverse proxy + auto SSL)
cat > /etc/caddy/Caddyfile << 'EOF'
your-domain.ru {
    reverse_proxy localhost:8000
    encode gzip
    
    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        Referrer-Policy strict-origin-when-cross-origin
    }
}
EOF

systemctl restart caddy
```

### Мониторинг (бесплатно)

```bash
# Простой мониторинг через cron
cat > /opt/neuroege/monitor.sh << 'EOF'
#!/bin/bash
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
MEM=$(free -m | awk 'NR==2{printf "%.1f", $3*100/$2}')
DISK=$(df -h / | awk 'NR==2{print $5}')

# Алерт если что-то критично
if (( $(echo "$MEM > 85" | bc -l) )); then
    curl -X POST "https://api.telegram.org/bot$TG_BOT/sendMessage" \
        -d "chat_id=$TG_CHAT&text=⚠️ NeuroEGE RAM: ${MEM}%"
fi
EOF
chmod +x /opt/neuroege/monitor.sh

# Каждые 5 минут
echo "*/5 * * * * /opt/neuroege/monitor.sh" | crontab -
```

### Бэкапы на встроенный HDD (120 GB)

```bash
# Ежедневный бэкап PostgreSQL
cat > /opt/neuroege/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/neuroege"
DATE=$(date +%Y%m%d_%H%M)

mkdir -p $BACKUP_DIR
pg_dump neuroege | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Храним последние 7 дней
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
EOF

chmod +x /opt/neuroege/backup.sh
echo "0 3 * * * /opt/neuroege/backup.sh" | crontab -
```

---

## 11. Roadmap инфраструктуры 2026 (ваш VPS)

### Почему сразу PostgreSQL (не SQLite)

| Проблема SQLite | Решение PostgreSQL 18 |
|-----------------|----------------------|
| Write lock на всю БД | Concurrent writes |
| Async ORM ограничен | Полная поддержка Django 6.0 async |
| Миграция данных потом | Не нужна |
| Нет io_uring | +50% I/O производительности |

При 5,000 учениках и ~1-2 writes/sec SQLite создаст bottleneck. PostgreSQL настраивается за 15 минут.

### Этапы

| Этап | Users | Архитектура | Доп. затраты |
|------|-------|-------------|--------------|
| **MVP** | 100 | VPS + PostgreSQL 18 + Qwen3 (free) | **0 ₽** |
| **Alpha** | 500 | VPS + PostgreSQL 18 + DeepSeek | **~300 ₽** |
| **Beta** | 2,000 | VPS + PostgreSQL 18 + DeepSeek | **~1,500 ₽** |
| **Год 1** | 5,000 | VPS + PostgreSQL 18 + DeepSeek/Gemini | **~2,500 ₽** |
| **Год 2** | 20,000 | VPS (апгрейд 8GB) + PG + Tiered LLM | **~10,000 ₽** |

### Когда апгрейдить VPS

```
Мониторинг:
├── RAM usage > 80% постоянно → апгрейд до 8 GB
├── CPU load > 2.5 постоянно → апгрейд CPU
├── Disk > 50 GB → чистка или апгрейд
└── Response time p95 > 1s → оптимизация или апгрейд

Hostiman тарифы (примерно):
├── RVDS3: 3 CPU, 4 GB  — текущий
├── RVDS4: 4 CPU, 8 GB  — ~1,500 ₽/мес (Год 2)
└── RVDS5: 6 CPU, 16 GB — ~3,000 ₽/мес (масштаб)
```

---

## 12. Сравнение: было vs стало (с вашим VPS)

| Аспект | Архитектура 2024 | **Ваша архитектура 2026** |
|--------|------------------|---------------------------|
| Backend | Django + Celery + Redis | Django 6.0 (встроенные Tasks) |
| DB | Managed PostgreSQL ($30+) | PostgreSQL 18 на VPS (**$0**) |
| Sandbox | Docker containers | subprocess + rlimit (**$0**) |
| LLM | GPT-4o ($2.50/$10) | DeepSeek V3 ($0.14/$0.28) |
| Hosting | Отдельный VPS | **Уже есть** (Hostiman) |
| CDN | Платный | Cloudflare Free |
| SSL | Платный | Caddy auto (**$0**) |
| **Год 1 доп.** | 8,000-70,000 ₽ | **500-3,500 ₽** |
| **Год 2 доп.** | 50,000-300,000 ₽ | **4,000-15,000 ₽** |

---

## 13. Риски и митигации

| Риск | Митигация 2026 |
|------|----------------|
| LLM downtime | Multi-provider: DeepSeek → Gemini → Qwen3 |
| Neon outage | Daily pg_dump в Cloudflare R2 |
| Modal limits | Fallback на Fly.io Machines |
| Vendor lock-in | Standard PostgreSQL, OpenAI-compatible APIs |
| Cold starts | Warm instances в пиковые часы |

---

## 14. Quick Start

```bash
# 1. Клонируем и настраиваем
git clone https://github.com/your/neuroege
cd neuroege

# 2. Переменные окружения
cp .env.example .env
# DATABASE_URL=postgres://user:pass@ep-xxx.neon.tech/neuroege
# DEEPSEEK_API_KEY=sk-xxx

# 3. Запуск (Python 3.13+, Django 6.0+)
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# 4. Production deploy
railway up  # или: render deploy
```

---

## Итог

**С вашим VPS + технологии 2026-27:**

| Метрика | Значение |
|---------|----------|
| Инфраструктура | **уже есть** (Hostiman RVDS3) |
| Доп. затраты MVP | **0 ₽** |
| Доп. затраты Год 1 | **500-3,500 ₽/мес** (только LLM) |
| Доп. затраты Год 2 | **4,000-15,000 ₽/мес** |
| Экономия vs классика | **90-95%** |

### Главные драйверы экономии

1. **Свой VPS** → нет платы за хостинг
2. **PostgreSQL 18 локально** → нет платы за managed DB
3. **Sandbox без Docker** → subprocess + rlimit экономит RAM
4. **Django 6.0 Tasks** → убираем Celery + Redis
5. **DeepSeek V3 / Qwen3** → LLM в 20-50 раз дешевле
6. **Cloudflare Free** → CDN бесплатно
7. **Caddy** → автоматический SSL бесплатно

### Архитектура на вашем VPS

```
┌─────────────────────────────────────────────────────────┐
│              Hostiman RVDS3 (уже есть)                  │
│  3 CPU × 3700 MHz │ 4 GB RAM │ 60 GB NVMe              │
├─────────────────────────────────────────────────────────┤
│  Caddy ──→ Django 6.0/Uvicorn ──→ PostgreSQL 18        │
│                 ↓                                       │
│         subprocess sandbox                              │
└─────────────────────────────────────────────────────────┘
                         ↓
              DeepSeek V3 / Qwen3 API
              ($0.14-0.28 / 1M tokens)
```

### Минимальный бюджет запуска

| Этап | Затраты/мес |
|------|-------------|
| MVP (100 users) | **0 ₽** (Qwen3 бесплатно) |
| Beta (2,000 users) | **~1,500 ₽** (DeepSeek) |
| Год 1 (5,000 users) | **~2,500 ₽** |
| Год 2 (20,000 users) | **~10,000 ₽** (+ апгрейд VPS) |
