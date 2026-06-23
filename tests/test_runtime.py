from __future__ import annotations

import json

import pytest

from bottleneck_capital.runtime import RunLockError, run_lock


def test_run_lock_blocks_concurrent_same_process(tmp_path):
    with run_lock(tmp_path, "sentinel"), pytest.raises(RunLockError), run_lock(
        tmp_path, "sentinel"
    ):
        pass


def test_run_lock_cleans_up_after_success(tmp_path):
    lock_path = tmp_path / "state" / "run_locks" / "sentinel.lock"

    with run_lock(tmp_path, "sentinel"):
        assert lock_path.exists()

    assert not lock_path.exists()


def test_run_lock_replaces_dead_pid_lock(tmp_path):
    lock_path = tmp_path / "state" / "run_locks" / "sentinel.lock"
    lock_path.parent.mkdir(parents=True)
    lock_path.write_text(
        json.dumps(
            {
                "process": "sentinel",
                "pid": 999999999,
                "started_at": "2099-01-01T00:00:00-05:00",
            }
        ),
        encoding="utf-8",
    )

    with run_lock(tmp_path, "sentinel"):
        assert lock_path.exists()
