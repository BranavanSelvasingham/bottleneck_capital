from __future__ import annotations

import os
import subprocess
from pathlib import Path

from bottleneck_capital.io import scalar_text


def effective_sec_user_agent(root: Path, explicit: str = "") -> str:
    value = scalar_text(explicit) or scalar_text(os.environ.get("BCAP_SEC_USER_AGENT"))
    if value:
        return value
    email = _git_config_email(root)
    if email:
        return f"Bottleneck Capital research automation {email}"
    return ""


def _git_config_email(root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "config", "user.email"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if completed.returncode != 0:
        return ""
    return scalar_text(completed.stdout)
