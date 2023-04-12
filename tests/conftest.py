"""
Pytest configuration.
"""
import pytest

from zycelium.zygote.api import ZygoteAPI


@pytest.fixture(scope="function", autouse=True)
async def api():
    """API fixture."""
    _api = ZygoteAPI()
    await _api.start("sqlite://:memory:")
    yield _api
    await _api.stop()
