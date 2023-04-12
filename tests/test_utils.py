"""
Test utils.
"""
from pathlib import Path
from zycelium.zygote.utils import secret_key


def test_secret_key(tmp_path: Path):
    secret = secret_key(tmp_path / "secret")
    assert secret is not None
    with open(tmp_path / "secret", "r") as f:
        assert f.read().strip() == secret
