"""
Cryptographic utilities.
"""
from pathlib import Path
from OpenSSL import crypto


def generate_self_signed_certificate(
    certificate_path: Path, key_path: Path, valid_years: int
) -> None:
    """
    Generate a self-signed certificate and private key.
    """
    # Create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)

    # Create a self-signed certificate
    certificate = crypto.X509()
    certificate.get_subject().C = "NA"
    certificate.get_subject().ST = "local"
    certificate.get_subject().L = "local"
    certificate.get_subject().O = "Zycelium"
    certificate.get_subject().OU = "Zygote"
    certificate.get_subject().CN = "localhost"
    certificate.add_extensions(
        [
            crypto.X509Extension(
                b"subjectAltName", False, b"DNS:localhost, DNS:zygote.local"
            )
        ]
    )
    certificate.set_serial_number(1000)
    certificate.gmtime_adj_notBefore(0)
    certificate.gmtime_adj_notAfter(valid_years * 365 * 24 * 60 * 60)
    certificate.set_issuer(certificate.get_subject())
    certificate.set_pubkey(k)
    certificate.sign(k, "sha512")

    # Save certificate and private key
    with open(certificate_path, "wt", encoding="utf-8") as certificate_file:
        certificate_file.write(
            crypto.dump_certificate(crypto.FILETYPE_PEM, certificate).decode("utf-8")
        )
    with open(key_path, "wt", encoding="utf-8") as key_file:
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))
