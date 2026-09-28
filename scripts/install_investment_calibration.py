from __future__ import annotations

import argparse
import os
from pathlib import Path

SKILL = "calibrate-investment-recommendations"
REVIEW_SKILLS = (
    "review-current-state-and-recommend-investment",
    "review-broad-market-outlook",
    "find-next-multibagger",
)
START = "<!-- bcap-calibration:start -->"
END = "<!-- bcap-calibration:end -->"
HOOK = f"""{START}
## Shared Investment Calibration

For Bottleneck Capital reviews, read and follow
[`$calibrate-investment-recommendations`](../{SKILL}/SKILL.md)
before choosing the action. Complete its lesson application, journal, and concise report
steps before the final answer. It supplements this workflow; it does not authorize trades,
tracked investment-decision changes, or automatic policy promotion.
{END}"""


def installation_plan(root: Path, skills_dir: Path) -> list[tuple[Path, str | None, str]]:
    source = (root / "skills" / SKILL / "SKILL.md").read_text(encoding="utf-8")
    target = skills_dir / SKILL / "SKILL.md"
    if target.is_symlink():
        raise ValueError(f"Inspect the existing symlink before installing: {target}")
    existing = target.read_text(encoding="utf-8") if target.exists() else None
    if existing is not None and existing != source:
        raise ValueError(f"Existing shared skill differs; review it manually: {target}")
    plan = [(target, existing, source)] if existing != source else []
    for name in REVIEW_SKILLS:
        path = skills_dir / name / "SKILL.md"
        if path.is_symlink():
            raise ValueError(f"Inspect the existing symlink before editing: {path}")
        text = path.read_text(encoding="utf-8")
        if START in text or END in text:
            if text.count(START) != 1 or text.count(END) != 1:
                raise ValueError(f"Malformed calibration hook: {path}")
            block = text[text.index(START) : text.index(END) + len(END)]
            if block != HOOK:
                raise ValueError(f"Calibration hook differs; review it manually: {path}")
        else:
            plan.append((path, text, text + "\n\n" + HOOK + "\n"))
    return plan


def install(plan: list[tuple[Path, str | None, str]]) -> None:
    for path, before, _ in plan:
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if path.is_symlink() or current != before:
            raise ValueError(f"File changed during installation: {path}")
    for path, before, after in plan:
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if path.is_symlink() or current != before:
            raise ValueError(f"File changed during installation: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(after, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install the shared skill and bounded review hooks."
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Write the verified installation plan."
    )
    args = parser.parse_args()
    try:
        plan = installation_plan(Path(__file__).resolve().parents[1], args.skills_dir)
        if args.apply:
            install(plan)
        for path, _, _ in plan:
            print(f"{'Updated' if args.apply else 'Needs installation'}: {path}")
        if not plan:
            print("Shared skill and all three review hooks match the repository.")
        return 0 if args.apply or not plan else 1
    except (OSError, ValueError) as exc:
        print(f"Installation stopped: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
