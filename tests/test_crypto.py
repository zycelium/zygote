"""
Test cryptographic utilities.
"""
from pathlib import Path
from OpenSSL import crypto
from zycelium.zygote.crypto import ensure_tls_certificate_chain


def test_ensure_tls_certificate_chain(tmp_path: Path):
    domain_name = "test.example.com"
    valid_days = 365
    app_dir = tmp_path

    paths = ensure_tls_certificate_chain(domain_name, app_dir, valid_days)

    assert paths.ca.exists()
    assert paths.key.exists()
    assert paths.cert.exists()

    with open(paths.key, "rb") as key_file:
        key_cert = crypto.load_certificate(crypto.FILETYPE_PEM, key_file.read())
        assert key_cert.get_subject().CN == domain_name

    with open(paths.cert, "rb") as cert_file:
        cert_cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_file.read())
        assert cert_cert.get_subject().CN == domain_name

