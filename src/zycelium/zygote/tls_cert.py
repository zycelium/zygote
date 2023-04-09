"""
Utility to generate self-signed certificate for TLS.
"""
from pathlib import Path
from OpenSSL import crypto


def generate_self_signed_cert(cert_path: Path, key_path: Path) -> None:
    """
    Generate a self-signed certificate and private key.
    """
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)

    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "NA"
    cert.get_subject().ST = "local"
    cert.get_subject().L = "local"
    cert.get_subject().O = "Zycelium"
    cert.get_subject().OU = "Zygote"
    cert.get_subject().CN = "localhost"
    cert.add_extensions(
        [
            crypto.X509Extension(
                b"subjectAltName", False, b"DNS:localhost, DNS:zygote.local"
            )
        ]
    )
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, "sha512")

    with open(cert_path, "wt", encoding="utf-8") as cert_file:
        cert_file.write(
            crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8")
        )
    with open(key_path, "wt", encoding="utf-8") as key_file:
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))
