"""Бизнес-логика для заданий с Python-кодом.

Этот модуль НЕ импортирует Django ORM.
Чистые функции для выполнения и проверки кода.
"""

import resource
import subprocess
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    returncode: int
    runtime: float
    error: str | None = None


FORBIDDEN_PATTERNS = [
    "os.system",
    "subprocess",
    "eval(",
    "exec(",
    "__import__",
    "open(",
    "file(",
    "input(",  # для безопасности
]


def check_code_safety(code: str) -> tuple[bool, str | None]:
    """Проверить код на опасные паттерны."""
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in code:
            return False, f"Запрещённый паттерн: {pattern}"
    return True, None


def run_code(
    code: str,
    stdin: str = "",
    timeout: int = 5,
    memory_mb: int = 256,
) -> ExecutionResult:
    """Выполнить Python-код в sandbox."""
    import time

    is_safe, error = check_code_safety(code)
    if not is_safe:
        return ExecutionResult(
            stdout="",
            stderr="",
            returncode=-1,
            runtime=0,
            error=error,
        )

    def set_limits():
        resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
        resource.setrlimit(
            resource.RLIMIT_AS,
            (memory_mb * 1024 * 1024, memory_mb * 1024 * 1024),
        )
        resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))

    start_time = time.perf_counter()

    try:
        result = subprocess.run(
            ["python3", "-c", code],
            input=stdin,
            capture_output=True,
            timeout=timeout,
            text=True,
            preexec_fn=set_limits,
            env={"PATH": "/usr/bin", "PYTHONPATH": ""},
        )
        runtime = time.perf_counter() - start_time

        return ExecutionResult(
            stdout=result.stdout[:10000],
            stderr=result.stderr[:10000],
            returncode=result.returncode,
            runtime=round(runtime, 3),
        )
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            stdout="",
            stderr="Превышено время выполнения",
            returncode=-1,
            runtime=timeout,
            error="timeout",
        )
    except Exception as e:
        return ExecutionResult(
            stdout="",
            stderr=str(e),
            returncode=-1,
            runtime=0,
            error=str(e),
        )


def run_tests(
    code: str,
    test_cases: list[dict],
    timeout: int = 5,
) -> dict:
    """Прогнать код через тестовые случаи."""
    results = []
    passed = 0

    for i, test in enumerate(test_cases):
        result = run_code(code, stdin=test.get("input", ""), timeout=timeout)

        expected = test.get("output", "").strip()
        actual = result.stdout.strip()
        is_pass = actual == expected and result.error is None

        if is_pass:
            passed += 1

        results.append({
            "test": i + 1,
            "passed": is_pass,
            "expected": expected,
            "actual": actual,
            "runtime": result.runtime,
            "error": result.error,
        })

    return {
        "total": len(test_cases),
        "passed": passed,
        "all_passed": passed == len(test_cases),
        "results": results,
    }
