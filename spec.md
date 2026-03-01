Отлично. Ниже — **чёткое, инженерно-ориентированное ТЗ**, которое можно **прямо скопировать в Cursor AI** и использовать как базу для генерации кода и архитектуры.
Фокус: **образовательный стартап + подготовка на 90+**, Python-задачи ЕГЭ (24–27).

---

# ТЕХНИЧЕСКОЕ ЗАДАНИЕ

## AI-тренажёр ЕГЭ по информатике (Python)

---

## 1. Цель продукта

Создать **десктоп-first веб-приложение** (PWA-ready), которое:

* анализирует **Python-решения учеников**
* объясняет **логику и мышление**
* адаптирует обучение под пользователя
* готовит к **90+ баллам ЕГЭ**

Приложение — не сборник задач, а **AI-репетитор с аналитикой мышления**.

---

## 2. Технологический стек (фиксированный)

### Backend

* **Django**
* **Django Ninja** (REST API)
* **SQLite** (MVP)
* **Celery (опционально позже)**

### Frontend

* HTML + CSS
* **HTMX**
* Alpine.js (минимально, по необходимости)
* Monaco Editor (Python)

### AI / LLM

* **LangChain**
* LLM (абстракция, модель меняемая)
* Prompt Templates
* Memory (per-user)

---

## 3. Архитектура (высокоуровнево)

```
Frontend (HTMX)
   ↓
Django + Ninja API
   ↓
Task Engine ─ Code Runner ─ Analyzer
   ↓
LangChain (LLM)
   ↓
Feedback / Hints / Trajectory
```

---

## 4. Основные сущности (Models)

### User

```python
id
email
password
created_at
level_estimate (float)
stress_level (float)
```

### Task

```python
id
number (24-27)
title
statement
input_description
output_description
difficulty (1–10)
concepts (list[str])
official_solution
```

### Attempt

```python
id
user_id
task_id
user_code
is_correct
runtime
memory
created_at
```

### AIAnalysis

```python
attempt_id
logic_errors
algorithm_type
complexity_estimate
feedback_text
suggested_approach
confidence_score
```

### SkillProfile

```python
user_id
skill_name
level (0–1)
last_updated
```

---

## 5. Ключевые фичи (обязательные)

---

## 5.1 Python Code Runner

**Требования:**

* запуск пользовательского Python-кода
* sandbox (ограничение времени и памяти)
* stdin / stdout
* защита от import os, sys, subprocess и т.д.

**Выход:**

```json
{
  "stdout": "...",
  "stderr": "...",
  "runtime": 0.23,
  "memory": 12.4
}
```

---

## 5.2 AI-анализ решения (killer feature)

После каждой попытки:

### LLM должен определить:

* тип решения:

  * перебор
  * оптимизированный перебор
  * математика
  * динамика
* логические ошибки
* граничные случаи
* асимптотику
* стиль мышления ученика

### Формат ответа LLM:

```json
{
  "algorithm_type": "bruteforce",
  "mistakes": ["ошибка границы диапазона"],
  "complexity": "O(n^2)",
  "feedback": "Ты правильно выбрал перебор, но...",
  "better_idea": "Можно сократить диапазон...",
  "confidence": 0.72
}
```

---

## 5.3 Режим «AI думает вслух»

Отдельная кнопка:

> «Показать, как думает эксперт»

AI:

1. анализирует условие
2. формулирует идею
3. отбрасывает плохие подходы
4. пишет псевдокод
5. только потом — Python

---

## 5.4 Уровневая система подсказок

Подсказки **не должны сразу раскрывать решение**.

Уровни:

1. идея
2. направление
3. структура алгоритма
4. почти готовый код

---

## 5.5 Генерация похожих задач

LLM получает:

* исходную задачу
* концепт
* сложность

Возвращает:

* 1–3 новых задач
* с уникальными условиями
* без повторения чисел

---

## 6. Персональная траектория (адаптация)

На основе Attempt + AIAnalysis:

AI решает:

* что давать дальше
* когда усложнять
* когда повторять
* когда включить «антистресс»

Пример:

```python
if user.stress_level > 0.7:
    give_easy_confidence_task()
```

---

## 7. UX (обязательно)

### Desktop UI

* экран = задача + редактор + вывод
* справа — AI-комментарии
* пошаговое выполнение
* тёмная тема

### HTMX-паттерны

* submit → partial update
* без перезагрузки страницы
* lazy load AI-разборов

---

## 8. API (пример)

```python
@router.post("/attempt/")
def submit_attempt(request, data: AttemptSchema):
    run_code()
    analyze()
    store()
    return AIAnalysisSchema
```

---

## 9. Prompt Engineering (важно)

### System Prompt (пример)

```
Ты — эксперт ЕГЭ по информатике.
Ты не даёшь готовое решение сразу.
Ты объясняешь мышление ученика.
Ты доброжелателен, но строг.
```

### Анализ должен:

* не использовать сложную математику без объяснений
* быть ориентирован на ученика 10–11 класса
* избегать «воды»

---

## 10. MVP (строго)

### MUST HAVE

* 10–15 задач (24–27)
* Python editor
* Code runner
* AI-анализ
* подсказки
* профиль ученика

### NOT IN MVP

* мобильное приложение
* соцфичи
* геймификация

---

## 11. Метрики успеха

* % учеников, решающих задачу со 2-й попытки
* рост confidence_score
* среднее время решения
* retention 7/30 дней

---

## 12. Что сказать Cursor AI (коротко)

> «Ты senior backend + AI engineer.
> Реализуй Django + Ninja проект по этому ТЗ.
> Код — production-ready.
> Архитектура — расширяемая.
> AI-часть — через LangChain.»

---

Если хочешь, дальше можем:

* разбить это ТЗ **на задачи для Cursor**
* написать **первые prompt templates**
* спроектировать **sandbox для Python**
* придумать **killer onboarding для учеников**

Скажи, что делаем следующим шагом 👇



стили серо-зеленые https://pytex.school/
https://kompege.ru/


https://solvit.space/
