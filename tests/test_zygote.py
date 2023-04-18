# pyright:  reportGeneralTypeIssues=false
# pylint: disable=no-member, missing-function-docstring, missing-module-docstring
from pathlib import Path
from zycelium import zygote


def test_zygote_version():
    assert zygote.version == "0.1.0"


def test_zygote_app_dir():
    assert isinstance(zygote.config.app_dir, Path)


def test_zygote_config_save_and_load(tmp_path: Path):
    temp_config_path = tmp_path / "zygote.conf"
    assert temp_config_path.exists() is False

    assert zygote.config.debug is False
    zygote.config.debug = True
    zygote.config.save(temp_config_path)
    assert temp_config_path.exists()

    zygote.config.load(temp_config_path)
    assert zygote.config.debug is True
