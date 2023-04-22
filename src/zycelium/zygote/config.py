"""
Zygote Configuration.
"""
from dataclasses import field
from pathlib import Path

import configobj
from click import get_app_dir
from passlib.hash import argon2

from zycelium.dataconfig import dataconfig

APP_DIR_PATH = Path(get_app_dir("zygote"))
APP_CONFIG_FILE = "zygote.conf"
APP_CONFIG_LOOKUP_PATHS = [".", str(APP_DIR_PATH), "/usr/local/etc"]


@dataconfig(file=APP_CONFIG_FILE, paths=APP_CONFIG_LOOKUP_PATHS)
class DefaultConfig:
    """Zygote Configuration"""

    debug: bool = False
    database_url: str = f"sqlite:///{APP_DIR_PATH}/zygote.db"

    admin_password: str = (
        "$argon2id$v=19$m=65536,t=3,"
        "p=4$07o3BkCIUcr5P4cQAmAMoQ$hhrChJnPrF8QFXO2eT6CZHSvkYLLVLVBEwIHxNpulOY"
    )  # "admin"

    http_host: str = "localhost"
    http_port: int = 3965

    ca_cert_file: str = f"{APP_DIR_PATH}/zygote_ca.pem"
    ca_key_file: str = f"{APP_DIR_PATH}/zygote_ca_key.pem"

    server_cert_file: str = f"{APP_DIR_PATH}/server_cert.pem"
    server_key_file: str = f"{APP_DIR_PATH}/server_key.pem"

    instance_name: str = "Zygote"
    instance_description: str = "Personal Automation Framework"
    instance_base_url: str = "https://zygote.local:3965"
    instance_verify_tls: bool = False

    server_identities: list = field(
        default_factory=lambda: [
            "zygote.local",
            "localhost",
            "127.0.0.1",
            "::1",
        ]
    )
    server_default_identity: str = "zygote.local"

    @property
    def app_dir(self):
        """OS-specific directory to store app data."""
        return APP_DIR_PATH

    @property
    def app_config(self):
        """Filename for app config."""
        return APP_CONFIG_FILE

    @property
    def app_config_path(self):
        """Full path to app config within lookup paths. If none exists, app_dir/app_config."""
        for lookup_path in APP_CONFIG_LOOKUP_PATHS:
            potential_config_path = Path(lookup_path) / APP_CONFIG_FILE
            if potential_config_path.exists():
                return potential_config_path
        return APP_DIR_PATH / APP_CONFIG_FILE

    def change_password(self, new_password: str):
        """Change admin password."""
        self.admin_password = argon2.hash(new_password)

    def check_password(self, password: str):
        """Check admin password."""
        return argon2.verify(password, self.admin_password)

    def ensure_app_dir(self):
        """Ensure app directory exists."""
        self.app_dir.mkdir(parents=True, exist_ok=True)


config = DefaultConfig()
ConfigParseError = configobj.UnreprError
