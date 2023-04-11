"""
Utilities.
"""
import secrets
from pathlib import Path


def secret_key(path: Path) -> str:
    """
    Get a secret key from a file.
    """
    if not path.exists():
        key = secrets.token_urlsafe(32)
        path.write_text(key)
    return path.read_text().strip()
