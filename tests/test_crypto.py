"""
Test cryptographic utilities.
"""
from pathlib import Path
from OpenSSL import crypto
from zycelium.zygote.crypto import generate_self_signed_certificate


async def test_generate_self_signed_certificate(tmp_path: Path) -> None:
    """
    Test generating a self-signed certificate.
    """
    cert_path = tmp_path / "cert.pem"
    key_path = tmp_path / "key.pem"
    generate_self_signed_certificate(cert_path, key_path, 1)
    assert cert_path.exists()
    assert key_path.exists()
    with open(cert_path, "rt", encoding="utf-8") as cert_file:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_file.read())  # type: ignore
    assert cert.get_subject().CN == "localhost"
    with open(key_path, "rt", encoding="utf-8") as key_file:
        key = crypto.load_privatekey(crypto.FILETYPE_PEM, key_file.read())
    assert key.bits() == 4096
    assert key.type() == crypto.TYPE_RSA
