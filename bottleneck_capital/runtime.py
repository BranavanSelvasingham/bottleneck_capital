from __future__ import annotations

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from bottleneck_capital.io import append_jsonl


class RunLockError(RuntimeError):
    """Raised when another active run owns the same process lock."""


@contextmanager
def run_lock(root: Path, process: str, *, stale_after_minutes: int = 45) -> Iterator[Path]:
    lock_path = root / "state" / "run_locks" / f"{process}.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    if lock_path.exists() and not _lock_is_stale(lock_path, stale_after_minutes):
        raise RunLockError(f"Active run lock exists for {process}: {lock_path}")
    payload = {
        "process": process,
        "pid": os.getpid(),
        "started_at": _now(),
    }
    lock_path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    try:
        yield lock_path
    finally:
        try:
            current = json.loads(lock_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            current = {}
        if current.get("pid") == os.getpid():
            lock_path.unlink(missing_ok=True)


def record_run(
    root: Path,
    *,
    process: str,
    command: str,
    status: str,
    started_at: str,
    ended_at: str | None = None,
    outputs: list[str] | None = None,
    warnings: list[str] | None = None,
    error: str = "",
) -> None:
    append_jsonl(
        root / "state" / "run_ledger.jsonl",
        {
            "process": process,
            "command": command,
            "status": status,
            "started_at": started_at,
            "ended_at": ended_at or _now(),
            "outputs": outputs or [],
            "warnings": warnings or [],
            "error": error,
        },
    )


def _lock_is_stale(path: Path, stale_after_minutes: int) -> bool:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return True
    pid = payload.get("pid")
    if isinstance(pid, int) and not _pid_exists(pid):
        return True
    started_at = payload.get("started_at")
    if not isinstance(started_at, str):
        return True
    try:
        started = datetime.fromisoformat(started_at)
    except ValueError:
        return True
    return _now_dt() - started > timedelta(minutes=stale_after_minutes)


def _pid_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _now() -> str:
    return _now_dt().isoformat(timespec="seconds")


def _now_dt() -> datetime:
    return datetime.now(ZoneInfo("America/Toronto"))
