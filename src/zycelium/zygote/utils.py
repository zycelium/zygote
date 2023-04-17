"""
Utilities.
"""
import json
import secrets
from pathlib import Path


def secret_key(path: Path) -> str:
    """
    Get a secret key from a file.
    """
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        key = secrets.token_urlsafe(32)
        path.write_text(key)
    return path.read_text().strip()


def py_string_to_dict(data_str: str) -> dict:
    """
    Convert a python string to a json string.
    """
    return json.loads(
        data_str.replace("'", '"')
        .replace("True", "true")
        .replace("False", "false")
        .replace("None", "null")
    )
