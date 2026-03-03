**готовые LangChain-классы**, которые можно **сразу класть в проект** (`ai_engine/`).


* **production-ready**
* с жёсткими схемами
* с разделением ответственности
* без «магии»

Стек: `langchain`, `langchain-openai`, `langchain-anthropic`, `pydantic`.

---

# 📁 Структура `ai_engine/`

```text
ai_engine/
 ├── llm_config.py
 ├── schemas.py
 ├── prompts.py
 ├── analyzer_chain.py
 ├── explain_chain.py
 ├── hint_chain.py
 ├── generator_chain.py
 └── checker_chain.py
```

---

# 1. llm_config.py — конфигурация моделей

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

analyzer_llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.1,
    max_tokens=800
)

tutor_llm = ChatAnthropic(
    model="claude-3.5-sonnet",
    temperature=0.4,
    max_tokens=1200
)

generator_llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.6,
    max_tokens=1000
)
```

---

# 2. schemas.py — строгие выходные схемы (CRITICAL)

```python
from pydantic import BaseModel
from typing import List, Optional


class AnalysisResult(BaseModel):
    algorithm_type: str
    mistakes: List[str]
    complexity: str
    feedback: str
    better_idea: Optional[str]
    confidence: float


class HintResult(BaseModel):
    level: int
    hint: str


class CheckResult(BaseModel):
    is_correct: bool
    error_explanation: Optional[str]


class GeneratedTask(BaseModel):
    expression: str
    table: list
```

---

# 3. prompts.py — все промты в одном месте

```python
SYSTEM_ANALYZER = """
Ты — эксперт ЕГЭ по информатике.
Ты анализируешь решения учеников.
Ты не угадываешь.
Ты возвращаешь ТОЛЬКО валидный JSON.
"""

ANALYZE_PROMPT = """
Условие задачи:
{task}

Решение ученика:
{code}

Проанализируй решение.
"""

SYSTEM_TUTOR = """
Ты — строгий, но доброжелательный репетитор ЕГЭ.
Ты объясняешь логику, а не просто ответ.
"""

EXPLAIN_PROMPT = """
Логическое выражение:
{expression}

Фрагмент таблицы:
{table}

Объясни решение пошагово.
"""

HINT_PROMPT = """
Условие задачи:
{task}

Уровень подсказки: {level}
(1 — идея, 2 — направление, 3 — структура, 4 — почти код)

Дай подсказку, не раскрывая решение.
"""

CHECK_PROMPT = """
Ученик дал ответ: {answer}

Правильный ответ: {correct}

Проверь корректность.
"""
```

---

# 4. analyzer_chain.py — AI-анализ решения (killer feature)

```python
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from .llm_config import analyzer_llm
from .schemas import AnalysisResult
from .prompts import SYSTEM_ANALYZER, ANALYZE_PROMPT


class SolutionAnalyzer:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=AnalysisResult)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_ANALYZER),
            ("human", ANALYZE_PROMPT)
        ])

        self.chain = self.prompt | analyzer_llm | self.parser

    def analyze(self, task: str, code: str) -> AnalysisResult:
        return self.chain.invoke({
            "task": task,
            "code": code
        })
```

---

# 5. explain_chain.py — режим «AI думает вслух»

```python
from langchain.prompts import ChatPromptTemplate
from .llm_config import tutor_llm
from .prompts import SYSTEM_TUTOR, EXPLAIN_PROMPT


class ExplainThinking:
    def __init__(self):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_TUTOR),
            ("human", EXPLAIN_PROMPT)
        ])
        self.chain = self.prompt | tutor_llm

    def explain(self, expression: str, table: str) -> str:
        return self.chain.invoke({
            "expression": expression,
            "table": table
        }).content
```

---

# 6. hint_chain.py — поуровневые подсказки

```python
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from .llm_config import tutor_llm
from .schemas import HintResult
from .prompts import SYSTEM_TUTOR, HINT_PROMPT


class HintGenerator:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=HintResult)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_TUTOR),
            ("human", HINT_PROMPT)
        ])

        self.chain = self.prompt | tutor_llm | self.parser

    def get_hint(self, task: str, level: int) -> HintResult:
        return self.chain.invoke({
            "task": task,
            "level": level
        })
```

---

# 7. generator_chain.py — генерация новых задач

```python
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from .llm_config import generator_llm
from .schemas import GeneratedTask


GENERATOR_PROMPT = """
Сгенерируй логическую функцию от 4 переменных
и полную таблицу истинности.
"""


class TaskGenerator:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=GeneratedTask)

        self.prompt = ChatPromptTemplate.from_messages([
            ("human", GENERATOR_PROMPT)
        ])

        self.chain = self.prompt | generator_llm | self.parser

    def generate(self) -> GeneratedTask:
        return self.chain.invoke({})
```

---

# 8. checker_chain.py — проверка ответа ученика

```python
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from .llm_config import analyzer_llm
from .schemas import CheckResult
from .prompts import SYSTEM_ANALYZER, CHECK_PROMPT


class AnswerChecker:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=CheckResult)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_ANALYZER),
            ("human", CHECK_PROMPT)
        ])

        self.chain = self.prompt | analyzer_llm | self.parser

    def check(self, answer: str, correct: str) -> CheckResult:
        return self.chain.invoke({
            "answer": answer,
            "correct": correct
        })
```

---

# 9. Как это использовать в Django

```python
analyzer = SolutionAnalyzer()
result = analyzer.analyze(task_text, user_code)

if not result.confidence > 0.5:
    fallback_to_auto_solver()
```

---

# 10. CTO-совет напоследок

✔ LLM **не решает задачу**, а **объясняет и анализирует**
✔ правильный ответ всегда подтверждён **алгоритмом**
✔ LangChain — слой, который можно заменить без боли

---

Если хочешь, дальше могу:

* встроить это в **Django Ninja endpoints**
* добавить **retry + fallback стратегии**
* сделать **batch-анализ попыток**
* написать **юнит-тесты для chains**

Скажи, что следующий шаг 👇
