"""
Cryptographic utilities.
"""
from datetime import datetime, timedelta
from collections import namedtuple
from pathlib import Path

import trustme


CertificatePaths = namedtuple("CertificatePaths", ["ca", "key", "cert"])


def ensure_tls_certificate_chain(
    domain_name: str, app_dir: Path, valid_days: int
) -> CertificatePaths:
    """
    Ensure that a TLS certificate chain exists for the given domain name.

    If the certificate chain does not exist, it will be created.
    """

    app_tls_ca_path = app_dir / "ca.pem"
    app_tls_key_path = app_dir / "key.pem"
    app_tls_cert_path = app_dir / "cert.pem"
    not_after = datetime.utcnow() + timedelta(days=valid_days)

    if (
        not app_tls_ca_path.exists()
        or not app_tls_key_path.exists()
        or not app_tls_cert_path.exists()
    ):
        ca = trustme.CA(organization_name="Zycelium", organization_unit_name="Zygote")
        server_cert = ca.issue_cert(
            domain_name, common_name=domain_name, not_after=not_after
        )

        ca.cert_pem.write_to_path(str(app_tls_ca_path))
        server_cert.private_key_and_cert_chain_pem.write_to_path(str(app_tls_key_path))
        server_cert.cert_chain_pems[0].write_to_path(str(app_tls_cert_path))

    return CertificatePaths(app_tls_ca_path, app_tls_key_path, app_tls_cert_path)
