from zycelium.dataconfig import dataconfig


@dataconfig
class AppConfig:
    """App config."""

    host: str = "localhost"
    port: int = 3965

    log_level: str = "info"

    tls_enable: bool = True
    tls_ca_path: str = "ca.pem"
    tls_cert_path: str = "cert.pem"
    tls_key_path: str = "key.pem"


app_config = AppConfig()
