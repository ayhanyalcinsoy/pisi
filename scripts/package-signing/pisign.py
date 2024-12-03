#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
    PiSi Package Signing Tools (Python 3 Version)
"""

import base64
import getpass
import os
import hashlib
import shlex
import subprocess
import sys
import tempfile
import zipfile

# ZipFile extensions
ZIP_FILES = ('.zip', '.pisi')

# Signature headers & extensions
HEADER = 'pisi-signed'
EXT_SIGN = 'sig'
EXT_CERT = 'crt'

# Signature validity
SIGN_OK, SIGN_NO, SIGN_SELF, SIGN_UNTRUSTED, SIGN_CORRUPTED = list(range(5))

# Certificate validity
CERT_OK, CERT_SELF, CERT_CORRUPTED = list(range(3))

# Certificate trustworthiness
CERT_TRUSTED, CERT_UNTRUSTED = list(range(2))


def sign_data(data, key_file, password_fd):
    """
        Signs data with given key.

        Arguments:
            data: Data to be signed (bytes)
            key_file: Private key
            password_fd: File that contains passphrase
        Returns:
            Signed data (binary)
    """
    # Go to the beginning of password file
    password_fd.seek(0)

    # Use OpenSSL to sign data
    command = f'/usr/bin/openssl dgst -sha1 -sign {key_file} -passin fd:{password_fd.fileno()}'
    command = shlex.split(command)

    pipe = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    signed_binary, _ = pipe.communicate(input=data)

    return signed_binary


def get_public_key(cert_file):
    """
        Extracts public key from certificate.

        Arguments:
            cert_file: Certificate
        Returns:
            Public key (bytes)
    """
    # Use OpenSSL to extract public key
    command = f'openssl x509 -inform pem -in {cert_file} -pubkey -noout'
    command = shlex.split(command)

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    key_ascii, _ = pipe.communicate()

    return key_ascii


def get_hash(cert_file):
    """
        Extracts hash from certificate.

        Arguments:
            cert_file: Certificate
        Returns:
            Hash (string)
    """
    # Use OpenSSL to extract hash
    command = f'openssl x509 -noout -in {cert_file} -hash'
    command = shlex.split(command)

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cert_hash, _ = pipe.communicate()

    return cert_hash.decode().strip()


def check_trust(cert_file, trust_dir):
    """
        Checks if certificate is trusted or not.

        Arguments:
            cert_file: Certificate
            trust_dir: Path to trust database.
        Returns:
            CERT_TRUSTED or CERT_UNTRUSTED
    """
    cert_hash = get_hash(cert_file)

    for filename in os.listdir(trust_dir):
        cert_path = os.path.join(trust_dir, filename)
        if os.path.exists(cert_path):
            if cert_hash == get_hash(cert_path):
                return CERT_TRUSTED
    return CERT_UNTRUSTED


def verify_certificate(cert_file):
    """
        Verifies a certificate.

        Arguments:
            cert_file: Certificate
        Returns:
            CERT_OK, CERT_SELF or CERT_CORRUPTED
    """
    # Use OpenSSL to verify certificate
    command = f'/usr/bin/openssl verify {cert_file}'
    command = shlex.split(command)

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, _ = pipe.communicate()
    lines = output.decode().split('\n')

    if len(lines) < 2:
        return CERT_CORRUPTED
    elif lines[1].startswith("error"):
        code = lines[1].split()[1]
        if code == '18':
            return CERT_SELF
        else:
            return CERT_CORRUPTED
    else:
        return CERT_OK


def verify_file(data_file, cert_file=None, signature_file=None, trust_dir=None):
    """
        Verifies signature of file signed with given certificate.

        If signature_file is not defined, data_file + ".sig" will
        be used.

        If cert_file is not defined, data_file + ".crt" will
        be used.

        Arguments:
            data_file: Original data file
            cert_file: Certificate (or None)
            signature_file: Signature file (or None)
            trust_dir: Path to trust database.
        Returns:
            SIGN_OK, SIGN_NO, SIGN_SELF, SIGN_UNTRUSTED or SIGN_CORRUPTED
    """
    # Sanitize before appending signature extension
    data_file = os.path.realpath(data_file)

    if not signature_file:
        signature_file = data_file + '.' + EXT_SIGN
    if not cert_file:
        cert_file = data_file + '.' + EXT_CERT
    if not os.path.exists(signature_file) or not os.path.exists(cert_file):
        return SIGN_NO

    # Verify certificate
    cert_validity = verify_certificate(cert_file)
    if cert_validity == CERT_CORRUPTED:
        return SIGN_CORRUPTED

    # Check trustworthiness of certificate
    if trust_dir is not None and check_trust(cert_file, trust_dir) == CERT_UNTRUSTED:
        return SIGN_UNTRUSTED

    # Keep public key in a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as pub_file:
        pub_file.write(get_public_key(cert_file))
        pub_file.flush()

        # Use OpenSSL to verify signature
        command = f'/usr/bin/openssl dgst -sha1 -verify {pub_file.name} -signature {signature_file} {data_file}'
        command = shlex.split(command)

        pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = pipe.wait()

    os.unlink(pub_file.name)  # Ensure temporary file is deleted

    if result == 0:
        if cert_validity == CERT_OK:
            return SIGN_OK
        else:
            return SIGN_SELF
    else:
        return SIGN_CORRUPTED


def verify_data(data, signature_data, trust_dir):
    """
        Verifies signature of data signed with given certificate.

        Arguments:
            data: Original data
            signature_data: Signature data from ZipFile
            trust_dir: Path to trust database.
        Returns:
            SIGN_OK, SIGN_NO, SIGN_SELF or SIGN_CORRUPTED
    """
    # Check header
    if not signature_data or not signature_data.startswith(HEADER.encode()):
        return SIGN_NO
    try:
        header, cert_ascii, signature_ascii = signature_data.decode().split(':')
    except ValueError:
        return SIGN_CORRUPTED

    if header != HEADER:
        return SIGN_CORRUPTED

    signature_binary = base64.b64decode(signature_ascii)
    cert_data = base64.b64decode(cert_ascii)

    with tempfile.NamedTemporaryFile(delete=False) as cert_file, \
            tempfile.NamedTemporaryFile(delete=False) as signature_file, \
            tempfile.NamedTemporaryFile(delete=False) as data_file:

        cert_file.write(cert_data)
        cert_file.flush()

        signature_file.write(signature_binary)
        signature_file.flush()

        data_file.write(data)
        data_file.flush()

        result = verify_file(data_file.name, cert_file.name, signature_file.name, trust_dir)

    os.unlink(cert_file.name)
    os.unlink(signature_file.name)
    os.unlink(data_file.name)

    return result

def sign_zipfile(filename, key_file, cert_file, password_fd):
    """
        Signs ZIP file with given key.

        Arguments:
            filename: File name to be signed
            key_file: Private key
            cert_file: Certificate
            password_fd: File that contains passphrase
    """
    with zipfile.ZipFile(filename, 'a') as zip_obj:
        # Get ZIP hashes and sign them
        hashes = get_zip_hashes(zip_obj)
        signed_binary = sign_data(hashes.encode(), key_file, password_fd)
        signed_ascii = base64.b64encode(signed_binary).decode()

        # Encode certificate
        with open(cert_file, 'rb') as cert_file_obj:
            cert_data = cert_file_obj.read()
        cert_ascii = base64.b64encode(cert_data).decode()

        # Add signed data as ZIP comment
        zip_obj.comment = f'{HEADER}:{cert_ascii}:{signed_ascii}'.encode()

        # Mark file as modified and save it
        zip_obj._didModify = True


def sign_file(filename, key_file, cert_file, password_fd):
    """
        Signs file with given key.

        Arguments:
            filename: File name to be signed
            key_file: Private key
            cert_file: Certificate
            password_fd: File that contains passphrase
    """
    with open(filename, 'rb') as file_obj:
        data = file_obj.read()
    signed_binary = sign_data(data, key_file, password_fd)

    with open(cert_file, 'rb') as cert_file_obj:
        cert_data = cert_file_obj.read()

    # Save certificate
    with open(f'{filename}.{EXT_CERT}', 'wb') as cert_out_file:
        cert_out_file.write(cert_data)

    # Save signed data
    with open(f'{filename}.{EXT_SIGN}', 'wb') as signed_out_file:
        signed_out_file.write(signed_binary)


def print_usage():
    """
        Prints usage information of application and exits.
    """
    print("Usage:")
    print(f"  {sys.argv[0]} sign <priv_key> <cert> <file1 ...>")
    print(f"  {sys.argv[0]} verify <trust_dir> <file1 ...>")
    sys.exit(1)


def main():
    """
        Main
    """

    try:
        operation = sys.argv[1]
    except IndexError:
        print_usage()

    if operation == 'sign':
        try:
            key_file = sys.argv[2]
            cert_file = sys.argv[3]
        except IndexError:
            print_usage()

        if len(sys.argv[4:]):
            # Keep password in a temporary file
            password = getpass.getpass()
            with tempfile.NamedTemporaryFile(delete=False) as password_fd:
                password_fd.write(password.encode())
                password_fd.flush()

                for filename in sys.argv[4:]:
                    if filename.endswith(ZIP_FILES):
                        sign_zipfile(filename, key_file, cert_file, password_fd)
                    else:
                        sign_file(filename, key_file, cert_file, password_fd)
                    print(f"Signed {filename} with {key_file}")

                # Destroy temporary file
                os.unlink(password_fd.name)
        else:
            print_usage()

    elif operation == 'verify':
        try:
            trust_dir = sys.argv[2]
        except IndexError:
            print_usage()

        if len(sys.argv[3:]):
            for filename in sys.argv[3:]:
                if filename.endswith(ZIP_FILES):
                    result = verify_zipfile(filename, trust_dir)
                else:
                    result = verify_file(filename, trust_dir)
                if result == SIGN_OK:
                    print(f"{filename} is signed by a trusted source.")
                elif result == SIGN_NO:
                    print(f"{filename} is unsigned.")
                elif result == SIGN_SELF:
                    print(f"{filename} is self-signed by a trusted source.")
                elif result == SIGN_UNTRUSTED:
                    print(f"{filename} is signed by an untrusted source.")
                else:
                    print(f"{filename} is corrupted.")
        else:
            print_usage()

    else:
        print_usage()


if __name__ == "__main__":
    sys.exit(main())
