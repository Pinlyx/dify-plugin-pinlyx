"""Helpers that turn Dify tool parameters into clean API payloads."""

from __future__ import annotations

from typing import Any


def text(value: Any) -> str | None:
    """Trimmed string, or None when empty."""
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def integer(value: Any, name: str, *, minimum: int | None = None, maximum: int | None = None) -> int | None:
    """Parse a number parameter (Dify delivers numbers as int or float)."""
    if value is None or value == "":
        return None
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a whole number.") from None
    if minimum is not None and number < minimum:
        raise ValueError(f"{name} must be at least {minimum}.")
    if maximum is not None and number > maximum:
        raise ValueError(f"{name} must be at most {maximum}.")
    return number


def number(value: Any, name: str) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a number.") from None


def csv_list(value: Any) -> list[str] | None:
    """'a, b ,c' -> ['a', 'b', 'c']; None when nothing is left."""
    raw = text(value)
    if raw is None:
        return None
    items = [part.strip() for part in raw.split(",") if part.strip()]
    return items or None


def drop_empty(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: val for key, val in payload.items() if val is not None}
