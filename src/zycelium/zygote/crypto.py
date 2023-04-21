"""
Cryptographic utilities for Zygote.
"""
import ipaddress
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import idna
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    NoEncryption,
    load_pem_private_key,
)
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


def x_name(org_name: str, org_unit_name: str, common_name: Optional[str]) -> x509.Name:
    """
    Convert a string to a X.509 name.
    """
    x_org_name = x509.NameAttribute(NameOID.ORGANIZATION_NAME, org_name)
    x_org_unit_name = x509.NameAttribute(
        NameOID.ORGANIZATIONAL_UNIT_NAME, org_unit_name
    )
    if common_name:
        x_common_name = x509.NameAttribute(NameOID.COMMON_NAME, common_name)
        return x509.Name([x_org_name, x_org_unit_name, x_common_name])
    return x509.Name([x_org_name, x_org_unit_name])


def x_identity(identity: str) -> x509.GeneralName:
    """
    Convert a string to a X.509 identity.
    """
    if "@" in identity:
        return x509.RFC822Name(identity)
    try:
        return x509.IPAddress(ipaddress.ip_address(identity))
    except ValueError:
        try:
            return x509.IPAddress(ipaddress.ip_network(identity))
        except ValueError:
            pass
    if identity.startswith("*."):
        return x509.DNSName(idna.encode(identity[2:], uts46=True).decode("ascii"))
    return x509.DNSName(idna.encode(identity, uts46=True).decode("ascii"))


class CertificateAuthority:
    """
    Certificate Authority.
    """

    def __init__(
        self,
        org_name: str = "Zycelium",
        org_unit_name: str = "Zygote",
        cert_path: Path = Path("zygote_ca.pem"),
        key_path: Path = Path("zygote_ca_key.pem"),
        valid_days: int = 365,
    ):
        self.org_name = org_name
        self.org_unit_name = org_unit_name
        self.cert_path = cert_path
        self.key_path = key_path
        self.valid_days = valid_days
        self.name = x_name(org_name, org_unit_name, None)
        self.ca_key = self.load_or_generate_ca_key(cert_path, key_path)
        self.ca_cert = self.load_or_generate_ca_cert(cert_path, key_path)

    def load_or_generate_ca_key(
        self, cert_path: Path, key_path: Path
    ) -> ec.EllipticCurvePrivateKey:
        """Load or generate a private key."""
        if cert_path.exists() and key_path.exists():
            with open(key_path, "rb") as key_file:
                return load_pem_private_key(key_file.read(), None)
        key = ec.generate_private_key(ec.SECP384R1())
        with open(key_path, "wb") as key_file:
            key_file.write(
                key.private_bytes(
                    Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()
                )
            )
        return key

    def load_or_generate_ca_cert(
        self, cert_path: Path, key_path: Path
    ) -> x509.Certificate:
        """Load or generate a certificate."""
        if cert_path.exists() and key_path.exists():
            with open(cert_path, "rb") as cert_file:
                return x509.load_pem_x509_certificate(cert_file.read())
        cert = (
            x509.CertificateBuilder()
            .subject_name(self.name)
            .issuer_name(self.name)
            .public_key(self.ca_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=self.valid_days))
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None), critical=True
            )
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(self.ca_key.public_key()),
                critical=False,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=True,
                    crl_sign=True,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .sign(self.ca_key, hashes.SHA256())
        )
        with open(cert_path, "wb") as cert_file:
            cert_file.write(cert.public_bytes(Encoding.PEM))
        return cert

    def ensure_server_certificate(
        self,
        identities: list[str],
        common_name: str,
        cert_path: Path = Path("zygote_server_cert.pem"),
        key_path: Path = Path("zygote_server_key.pem"),
        valid_days: int = 365,
    ) -> x509.Certificate:
        """Load or generate a server certificate."""
        if cert_path.exists() and key_path.exists():
            with open(cert_path, "rb") as cert_file:
                return x509.load_pem_x509_certificate(cert_file.read())
        server_key = ec.generate_private_key(ec.SECP384R1())
        with open(key_path, "wb") as server_key_file:
            server_key_file.write(
                server_key.private_bytes(
                    Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()
                )
            )
        cert = (
            x509.CertificateBuilder()
            .subject_name(x_name(self.org_name, self.org_unit_name, common_name))
            .issuer_name(self.name)
            .public_key(server_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=valid_days))
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(server_key.public_key()),
                critical=False,
            )
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None), critical=True
            )
            .add_extension(
                x509.SubjectAlternativeName([x_identity(i) for i in identities]),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=True,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .add_extension(
                x509.ExtendedKeyUsage(
                    [
                        ExtendedKeyUsageOID.CLIENT_AUTH,
                        ExtendedKeyUsageOID.SERVER_AUTH,
                        ExtendedKeyUsageOID.CODE_SIGNING,
                    ]
                ),
                critical=True,
            )
            .sign(self.ca_key, hashes.SHA256())
        )
        with open(cert_path, "wb") as cert_file:
            cert_file.write(cert.public_bytes(Encoding.PEM))
        return cert
