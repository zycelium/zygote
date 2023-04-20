# pyright:  reportGeneralTypeIssues=false
# pylint: disable=no-member, missing-function-docstring, missing-module-docstring, invalid-name
import ipaddress
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)

from zycelium.zygote.crypto import (
    x_identity,
    x_name,
    CertificateAuthority,
)


def test_x_identity():
    assert x_identity("example@example.com") == x509.RFC822Name("example@example.com")
    assert x_identity("test") == x509.DNSName("test")
    assert x_identity("*.test") == x509.DNSName("test")
    assert x_identity("127.0.0.1") == x509.IPAddress(ipaddress.ip_address("127.0.0.1"))
    assert x_identity("127.0.1.0/24") == x509.IPAddress(
        ipaddress.ip_network("127.0.1.0/24")
    )


def test_x_name():
    assert x_name("Zycelium", "Zygote", None) == x509.Name(
        [
            x509.NameAttribute(x509.oid.NameOID.ORGANIZATION_NAME, "Zycelium"),
            x509.NameAttribute(x509.oid.NameOID.ORGANIZATIONAL_UNIT_NAME, "Zygote"),
        ]
    )
    assert x_name("Zycelium", "Zygote", "test") == x509.Name(
        [
            x509.NameAttribute(x509.oid.NameOID.ORGANIZATION_NAME, "Zycelium"),
            x509.NameAttribute(x509.oid.NameOID.ORGANIZATIONAL_UNIT_NAME, "Zygote"),
            x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, "test"),
        ]
    )


def test_certificate_authority(tmp_path: Path):
    ca = CertificateAuthority(
        cert_path=tmp_path / "ca.pem", key_path=tmp_path / "ca_key.pem"
    )
    assert ca.name == x509.Name(
        [
            x509.NameAttribute(x509.oid.NameOID.ORGANIZATION_NAME, "Zycelium"),
            x509.NameAttribute(x509.oid.NameOID.ORGANIZATIONAL_UNIT_NAME, "Zygote"),
        ]
    )
    assert ca.ca_key is not None
    assert ca.ca_cert is not None


def test_certificate_authority_load(tmp_path: Path):
    ca = CertificateAuthority(
        cert_path=tmp_path / "ca.pem", key_path=tmp_path / "ca_key.pem"
    )
    ca_key = ca.load_or_generate_ca_key(ca.cert_path, ca.key_path)
    ca_cert = ca.load_or_generate_ca_cert(ca.cert_path, ca.key_path)
    assert ca_key is not None
    assert ca_cert is not None
    assert ca_key.public_key().public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
    ) == ca_cert.public_key().public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
    )
    assert ca.ca_key.public_key().public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
    ) == ca_cert.public_key().public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
    )


def test_certificate_authority_server_certificate(tmp_path: Path):
    ca = CertificateAuthority(
        cert_path=tmp_path / "ca.pem", key_path=tmp_path / "ca_key.pem"
    )
    server_cert = ca.ensure_server_certificate(
        "localhost", "127.0.0.1", common_name="test.local"
    )
    assert server_cert is not None
    assert server_cert.subject == x509.Name(
        [
            x509.NameAttribute(x509.oid.NameOID.ORGANIZATION_NAME, "Zycelium"),
            x509.NameAttribute(x509.oid.NameOID.ORGANIZATIONAL_UNIT_NAME, "Zygote"),
            x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, "test.local"),
        ]
    )
    assert server_cert.issuer == x509.Name(
        [
            x509.NameAttribute(x509.oid.NameOID.ORGANIZATION_NAME, "Zycelium"),
            x509.NameAttribute(x509.oid.NameOID.ORGANIZATIONAL_UNIT_NAME, "Zygote"),
        ]
    )
    assert server_cert.extensions.get_extension_for_class(
        x509.SubjectAlternativeName
    ).value.get_values_for_type(x509.DNSName) == ["localhost"]
