from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

try:
    import yaml as _yaml
except ModuleNotFoundError:  # pragma: no cover - exercised when PyYAML is absent.
    _yaml = None


class ConfigError(ValueError):
    """Raised when project configuration cannot be parsed."""


def load_yaml_file(path: Path) -> Any:
    if not path.exists():
        raise ConfigError(f"Missing YAML file: {path}")
    return load_yaml_text(path.read_text(encoding="utf-8"))


def load_yaml_text(text: str) -> Any:
    if _yaml is not None:
        loaded = _yaml.safe_load(text)
        return {} if loaded is None else loaded
    return _simple_load_yaml(text)


def dump_yaml_mapping(mapping: Mapping[str, Any]) -> str:
    lines: list[str] = []
    for key, value in mapping.items():
        lines.extend(_dump_yaml_value(key, value, 0))
    return "\n".join(lines) + "\n"


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        raise ConfigError("Markdown frontmatter starts with --- but is not closed")
    frontmatter = parts[0].removeprefix("---\n")
    body = parts[1]
    loaded = load_yaml_text(frontmatter)
    if not isinstance(loaded, dict):
        raise ConfigError("Markdown frontmatter must be a mapping")
    return loaded, body


def read_markdown_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    if not path.exists():
        return {}, ""
    return parse_frontmatter(path.read_text(encoding="utf-8"))


def write_markdown_with_frontmatter(path: Path, frontmatter: Mapping[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\n{dump_yaml_mapping(frontmatter)}---\n{body.lstrip()}",
        encoding="utf-8",
    )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            loaded = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
        if not isinstance(loaded, dict):
            raise ConfigError(f"JSONL record at {path}:{line_number} must be an object")
        records.append(loaded)
    return records


def append_jsonl(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def read_json_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    if path.suffix == ".jsonl":
        return read_jsonl(path)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(loaded, dict) and isinstance(loaded.get("events"), list):
        loaded = loaded["events"]
    if not isinstance(loaded, list):
        raise ConfigError(f"Event file must contain a list or an events list: {path}")
    if not all(isinstance(item, dict) for item in loaded):
        raise ConfigError(f"Every event in {path} must be an object")
    return loaded


def scalar_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, int | float):
        return value != 0
    text = str(value).strip().lower()
    return text in {"true", "yes", "y", "1", "active", "triggered", "approved", "intact"}


def scalar_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for index, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:index].rstrip()
    return line.rstrip()


def _simple_load_yaml(text: str) -> Any:
    lines: list[tuple[int, str]] = []
    for raw_line in text.splitlines():
        line = _strip_comment(raw_line)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        lines.append((indent, line.strip()))
    if not lines:
        return {}
    value, index = _parse_yaml_block(lines, 0, lines[0][0])
    if index != len(lines):
        raise ConfigError(f"Could not parse YAML near: {lines[index][1]}")
    return value


def _parse_yaml_block(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines):
        return {}, index
    current_indent, content = lines[index]
    if current_indent < indent:
        return {}, index
    if content.startswith("- "):
        return _parse_yaml_sequence(lines, index, current_indent)
    return _parse_yaml_mapping(lines, index, current_indent)


def _parse_yaml_mapping(
    lines: list[tuple[int, str]], index: int, indent: int
) -> tuple[dict[str, Any], int]:
    mapping: dict[str, Any] = {}
    while index < len(lines):
        current_indent, content = lines[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ConfigError(f"Unexpected indentation near: {content}")
        if content.startswith("- "):
            break
        key, value_text = _split_key_value(content)
        index += 1
        if value_text == "":
            if index < len(lines) and lines[index][0] > current_indent:
                value, index = _parse_yaml_block(lines, index, lines[index][0])
            else:
                value = ""
        else:
            value = _parse_scalar(value_text)
        mapping[key] = value
    return mapping, index


def _parse_yaml_sequence(
    lines: list[tuple[int, str]], index: int, indent: int
) -> tuple[list[Any], int]:
    sequence: list[Any] = []
    while index < len(lines):
        current_indent, content = lines[index]
        if current_indent < indent:
            break
        if current_indent != indent or not content.startswith("- "):
            break
        item_text = content[2:].strip()
        index += 1
        if item_text == "":
            if index < len(lines) and lines[index][0] > current_indent:
                item, index = _parse_yaml_block(lines, index, lines[index][0])
            else:
                item = None
        elif ":" in item_text and not item_text.startswith(("'", '"')):
            key, value_text = _split_key_value(item_text)
            item = {key: _parse_scalar(value_text) if value_text else {}}
            if index < len(lines) and lines[index][0] > current_indent:
                nested, index = _parse_yaml_block(lines, index, lines[index][0])
                if isinstance(nested, dict):
                    item.update(nested)
                else:
                    item[key] = nested
        else:
            item = _parse_scalar(item_text)
        sequence.append(item)
    return sequence, index


def _split_key_value(content: str) -> tuple[str, str]:
    if ":" not in content:
        raise ConfigError(f"Expected key/value pair near: {content}")
    key, value = content.split(":", 1)
    key = key.strip()
    if not key:
        raise ConfigError(f"Missing YAML key near: {content}")
    return key, value.strip()


def _parse_scalar(value: str) -> Any:
    if value == "":
        return ""
    if value in {"[]", "{}"}:
        return [] if value == "[]" else {}
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    lowered = value.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    if lowered in {"null", "none", "~"}:
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def _dump_yaml_value(key: str, value: Any, indent: int) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        lines = [f"{prefix}{key}:"]
        for child_key, child_value in value.items():
            lines.extend(_dump_yaml_value(str(child_key), child_value, indent + 2))
        return lines
    if isinstance(value, list):
        lines = [f"{prefix}{key}:"]
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{prefix}  -")
                for child_key, child_value in item.items():
                    lines.extend(_dump_yaml_value(str(child_key), child_value, indent + 4))
            else:
                lines.append(f"{prefix}  - {_format_scalar(item)}")
        return lines
    return [f"{prefix}{key}: {_format_scalar(value)}"]


def _format_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    text = str(value)
    if text == "" or text.strip() != text or ": " in text or text.startswith(("{", "[", "#")):
        return json.dumps(text)
    return text
