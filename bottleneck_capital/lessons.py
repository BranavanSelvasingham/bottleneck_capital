from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from bottleneck_capital.io import load_yaml_file

REGISTER = Path("research/learning/lessons.yaml")
FIELDS = {
    "id",
    "version",
    "status",
    "title",
    "problem",
    "applies_when",
    "rule",
    "counterexamples",
    "evidence",
    "forward_test",
    "retire_if",
    "evaluation_ref",
    "change_note",
}


class LessonError(ValueError):
    """The lesson register or its application is not auditable."""


def load_lessons(root: Path) -> dict[str, dict[str, Any]]:
    try:
        data = load_yaml_file(root / REGISTER)
    except Exception as exc:
        raise LessonError(f"Cannot read lesson register: {REGISTER}") from exc
    if (
        not isinstance(data, dict)
        or set(data) != {"schema_version", "lessons"}
        or type(data["schema_version"]) is not int
        or data["schema_version"] != 1
        or not isinstance(data["lessons"], list)
        or not data["lessons"]
    ):
        raise LessonError("Invalid lesson register schema")
    lessons = {}
    for item in data["lessons"]:
        if not isinstance(item, dict) or set(item) != FIELDS:
            raise LessonError("Lesson has missing or unsupported fields")
        if not isinstance(item["id"], str) or not re.fullmatch(r"L\d{3,}", item["id"]):
            raise LessonError("Invalid lesson ID")
        if item["id"] in lessons:
            raise LessonError("Duplicate lesson ID")
        if type(item["version"]) is not int or item["version"] < 1:
            raise LessonError("Lesson version must be a positive integer")
        if item["status"] not in ("PROVISIONAL", "SUPPORTED", "RETIRED"):
            raise LessonError("Invalid lesson status")
        for field in FIELDS - {"version", "counterexamples", "evidence", "evaluation_ref"}:
            if not isinstance(item[field], str) or not item[field].strip():
                raise LessonError(f"Lesson requires nonempty {field}")
        for field in ("counterexamples", "evidence"):
            if (
                not isinstance(item[field], list)
                or not item[field]
                or any(not isinstance(value, str) or not value.strip() for value in item[field])
            ):
                raise LessonError(f"Lesson requires nonempty {field}")
        ref = item["evaluation_ref"]
        if not isinstance(ref, str):
            raise LessonError("evaluation_ref must be text")
        if item["status"] == "SUPPORTED" and not ref:
            raise LessonError("SUPPORTED requires a privacy-safe prospective evaluation note")
        if ref:
            path = (root / ref).resolve()
            if (
                Path(ref).is_absolute()
                or not path.is_relative_to(root.resolve())
                or not path.is_file()
            ):
                raise LessonError("evaluation_ref must name an existing note inside the repository")
        lessons[item["id"]] = item
    return lessons


def application_snapshots(root: Path, applications: Any) -> list[dict[str, Any]]:
    if not isinstance(applications, list) or not applications:
        raise LessonError("Record at least one relevant lesson application or explicit rejection")
    lessons = load_lessons(root)
    snapshots = []
    seen = set()
    for item in applications:
        if not isinstance(item, dict) or set(item) != {"id", "version", "disposition", "effect"}:
            raise LessonError("Lesson application has missing or unsupported fields")
        if not isinstance(item["id"], str) or item["id"] not in lessons:
            raise LessonError("Unknown lesson ID")
        lesson = lessons[item["id"]]
        if type(item["version"]) is not int or item["version"] != lesson["version"]:
            raise LessonError("Use the current lesson version")
        if item["id"] in seen:
            raise LessonError("Duplicate lesson application")
        seen.add(item["id"])
        if item["disposition"] not in ("APPLIED", "NOT_APPLICABLE", "COUNTEREVIDENCE"):
            raise LessonError("Invalid lesson disposition")
        if not isinstance(item["effect"], str) or not item["effect"].strip():
            raise LessonError("Explain the effect or reason for rejecting the lesson")
        if lesson["status"] == "RETIRED" and item["disposition"] == "APPLIED":
            raise LessonError("A retired lesson cannot be applied as an active rule")
        snapshots.append(lesson)
    return snapshots


def render_lessons(root: Path) -> list[str]:
    rows = ["## Lessons Register", "", "Provisional lessons are not proven return improvements."]
    for lesson in load_lessons(root).values():
        rows.append(
            f"- {lesson['id']} v{lesson['version']} / {lesson['status']} / "
            f"{lesson['title']}: {lesson['rule']}"
        )
    return [*rows, ""]
