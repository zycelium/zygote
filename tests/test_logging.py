"""
Test logging.
"""
from zycelium.zygote.logging import get_logger


def test_logging():
    """
    Test logging.
    """
    log = get_logger("zygote.test")
    assert log.name == "zygote.test"
