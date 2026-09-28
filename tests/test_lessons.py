from __future__ import annotations

from pathlib import Path

import pytest

import bottleneck_capital.io as io
from bottleneck_capital.lessons import REGISTER, LessonError, application_snapshots, load_lessons
from bottleneck_capital.validation import _check_lesson_register
from scripts.install_investment_calibration import (
    HOOK,
    REVIEW_SKILLS,
    SKILL,
    START,
    install,
    installation_plan,
)

ROOT = Path(__file__).parents[1]


def register_at(root: Path, text: str | None = None) -> Path:
    path = root / REGISTER
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text or (ROOT / REGISTER).read_text(), encoding="utf-8")
    return path


def test_seed_lessons_are_provisional_and_have_counterevidence() -> None:
    lessons = load_lessons(ROOT)
    assert len(lessons) == 6
    assert all(item["status"] == "PROVISIONAL" for item in lessons.values())
    assert all(item["counterexamples"] and item["forward_test"] for item in lessons.values())


def test_registry_works_with_dependency_free_yaml_fallback(monkeypatch) -> None:
    expected = load_lessons(ROOT)
    assert expected["L001"]["evidence"][-1].endswith("#entry-and-waiting")
    monkeypatch.setattr(io, "_yaml", None)
    assert load_lessons(ROOT) == expected


def test_supported_requires_repository_evaluation(tmp_path: Path) -> None:
    path = register_at(tmp_path)
    path.write_text(path.read_text().replace("PROVISIONAL", "SUPPORTED", 1))
    with pytest.raises(LessonError, match="prospective evaluation"):
        load_lessons(tmp_path)


def test_retired_rule_cannot_be_applied(tmp_path: Path) -> None:
    path = register_at(tmp_path)
    path.write_text(path.read_text().replace("PROVISIONAL", "RETIRED", 1))
    item = {"id": "L001", "version": 1, "disposition": "APPLIED", "effect": "Testing"}
    with pytest.raises(LessonError, match="retired"):
        application_snapshots(tmp_path, [item])
    item["disposition"] = "NOT_APPLICABLE"
    assert application_snapshots(tmp_path, [item])[0]["status"] == "RETIRED"


def test_duplicate_ids_and_private_fields_are_rejected(tmp_path: Path) -> None:
    text = (ROOT / REGISTER).read_text()
    register_at(tmp_path, text.replace("id: L002", "id: L001"))
    with pytest.raises(LessonError, match="Duplicate"):
        load_lessons(tmp_path)
    register_at(tmp_path, text.replace("    version: 1", "    quantity: 10\n    version: 1", 1))
    with pytest.raises(LessonError, match="unsupported"):
        load_lessons(tmp_path)


def test_validation_surfaces_bad_lesson_register(tmp_path: Path) -> None:
    register_at(tmp_path, "schema_version: 1\nlessons: []\n")
    issues = []
    _check_lesson_register(tmp_path, issues)
    assert any(issue.code == "LESSON_REGISTER_INVALID" for issue in issues)


def prepare_skills(root: Path) -> dict[Path, str]:
    contents = {}
    for name in REVIEW_SKILLS:
        path = root / name / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        contents[path] = f"---\nname: {name}\ndescription: Existing skill\n---\nKeep this text.\n"
        path.write_text(contents[path], encoding="utf-8")
    return contents


def test_installation_preserves_existing_skills_and_is_idempotent(tmp_path: Path) -> None:
    originals = prepare_skills(tmp_path)
    install(installation_plan(ROOT, tmp_path))
    assert (tmp_path / SKILL / "SKILL.md").read_text() == (
        ROOT / "skills" / SKILL / "SKILL.md"
    ).read_text()
    for path, original in originals.items():
        assert path.read_text() == original + "\n\n" + HOOK + "\n"
    assert installation_plan(ROOT, tmp_path) == []


def test_installation_does_not_partially_write_when_skill_missing(tmp_path: Path) -> None:
    prepare_skills(tmp_path)
    (tmp_path / REVIEW_SKILLS[-1] / "SKILL.md").unlink()
    with pytest.raises(FileNotFoundError):
        installation_plan(ROOT, tmp_path)
    assert not (tmp_path / SKILL).exists()


def test_installation_rejects_drift_and_concurrent_edits(tmp_path: Path) -> None:
    originals = prepare_skills(tmp_path)
    plan = installation_plan(ROOT, tmp_path)
    first = next(iter(originals))
    first.write_text(first.read_text() + "User edit\n")
    with pytest.raises(ValueError, match="File changed"):
        install(plan)
    assert "User edit" in first.read_text()
    assert not (tmp_path / SKILL).exists()
    first.write_text(first.read_text() + START)
    with pytest.raises(ValueError, match="Malformed"):
        installation_plan(ROOT, tmp_path)
