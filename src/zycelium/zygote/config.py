"""
Zygote Configuration.
"""
from pathlib import Path

import configobj
from click import get_app_dir

from zycelium.dataconfig import dataconfig as _dataconfig

app_dir_path = Path(get_app_dir("zygote"))  # pylint: disable=invalid-name
app_config_file = "zygote.conf"  # pylint: disable=invalid-name
app_config_lookup_paths = [".", str(app_dir_path), "/usr/local/etc"]


@_dataconfig(file=app_config_file, paths=app_config_lookup_paths)
class Config:
    """Zygote Configuration"""

    debug: bool = False

    @property
    def app_dir(self):
        """OS-specific directory to store app data."""
        return app_dir_path

    @property
    def app_config(self):
        """Filename for app config."""
        return app_config_file

    @property
    def app_config_path(self):
        """Full path to app config within lookup paths. If none exists, app_dir/app_config."""
        for lookup_path in app_config_lookup_paths:
            potential_config_path = Path(lookup_path) / app_config_file
            if potential_config_path.exists():
                return potential_config_path
        return app_dir_path / app_config_file


config = Config()
ConfigParseError = configobj.UnreprError
