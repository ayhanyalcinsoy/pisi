#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# pisi-key script adopted from apt-key
#
# Author : Serdar Dalgic - serdar AT pardus DOT org DOT tr
# Any comments are welcomed
#

import sys
import os
import subprocess

# GPG base command
GPG_CMD = 'gpg --ignore-time-conflict --no-options --no-default-keyring \
            --secret-keyring /etc/pisi/secring.gpg --trustdb-name /etc/pisi/trustdb.gpg'

MASTER_KEYRING = ''
ARCHIVE_KEYRING_URI = ''
ARCHIVE_KEYRING = '/usr/share/keyrings/pardus-archive-keyring.gpg'
REMOVED_KEYS = '/usr/share/keyrings/pardus-archive-removed-keys.gpg'

def execute_command(command):
    """Helper function to execute shell commands."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        result.check_returncode()
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.stderr}")
        sys.exit(1)

def addKey(GPG, keyfile):
    """Add a key to the keyring."""
    cmd = f"{GPG} --quiet --batch --import {keyfile}"
    print(f"cmd: {cmd}")
    execute_command(cmd)
    print(f"Key in {keyfile} is successfully added.")

def removeKey(GPG, keyfile):
    """Remove a key from the keyring."""
    cmd = f"{GPG} --quiet --batch --delete-key --yes {keyfile}"
    print(f"cmd: {cmd}")
    execute_command(cmd)
    print(f"Key in {keyfile} is successfully deleted.")

def update(GPG):
    """Update keys using the keyring package."""
    if not os.path.exists(ARCHIVE_KEYRING):
        print("ERROR: Can't find the archive-keyring")
        print("Is the pisi-archive-keyring package installed?")
        sys.exit(1)

    cmd = f"{GPG_CMD} --quiet --batch --keyring {ARCHIVE_KEYRING} --export | {GPG} --import"
    print(f"cmd: {cmd}")
    execute_command(cmd)

    if os.path.exists(REMOVED_KEYS):
        cmd = f"{GPG_CMD} --keyring {REMOVED_KEYS} --with-colons --list-keys | grep ^pub | cut -d: -f5"
        keys = execute_command(cmd).splitlines()
        for key in keys:
            cmd = f"{GPG} --quiet --batch --delete-key --yes {key}"
            execute_command(cmd)
    else:
        print(f"Warning: removed keys keyring {REMOVED_KEYS} missing or not readable")

def list_keys(GPG):
    """List keys."""
    cmd = f"{GPG} --batch --list-keys"
    print(f"cmd: {cmd}")
    print(execute_command(cmd))

def list_fingerprints(GPG):
    """List fingerprints."""
    cmd = f"{GPG} --batch --fingerprint"
    print(f"cmd: {cmd}")
    print(execute_command(cmd))

def export_key(GPG, keyid):
    """Export a specific key."""
    cmd = f"{GPG} --armor --export {keyid}"
    print(f"cmd: {cmd}")
    print(execute_command(cmd))

def exportAll(GPG):
    """Export all trusted keys."""
    cmd = f"{GPG} --armor --export"
    print(f"cmd: {cmd}")
    print(execute_command(cmd))

def printUsage():
    """Print usage information."""
    print("Usage: pisi-key [--keyring file] [command] [arguments]")
    print()
    print("Manage pisi's list of trusted keys")
    print()
    print("  pisi-key add <file>          - add the key contained in <file> ('-' for stdin)")
    print("  pisi-key del <keyid>         - remove the key <keyid>")
    print("  pisi-key export <keyid>      - output the key <keyid>")
    print("  pisi-key exportall           - output all trusted keys")
    print("  pisi-key update              - update keys using the keyring package")
    print("  pisi-key list                - list keys")
    print("  pisi-key finger              - list fingerprints")
    print()
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        printUsage()

    argc = 1

    if sys.argv[argc] == '--keyring':
        argc += 1
        keyring = sys.argv[argc]
        if not os.path.exists(keyring):
            print(f"Error: The specified keyring {keyring} is missing or not readable")
            sys.exit(1)
        argc += 1
        GPG_CMD += f" --keyring {keyring} --primary-keyring {keyring}"
    else:
        keyring = '/etc/pisi/trusted.gpg'
        if os.path.exists(keyring):
            GPG_CMD += f" --keyring {keyring} --primary-keyring {keyring}"

    operation = sys.argv[argc]
    argc += 1

    if operation == 'add':
        keyfile = sys.argv[argc]
        addKey(GPG_CMD, keyfile)

    elif operation == 'del':
        keyfile = sys.argv[argc]
        removeKey(GPG_CMD, keyfile)

    elif operation == 'update':
        update(GPG_CMD)

    elif operation == 'list':
        list_keys(GPG_CMD)

    elif operation == 'finger':
        list_fingerprints(GPG_CMD)

    elif operation == 'export':
        keyid = sys.argv[argc]
        export_key(GPG_CMD, keyid)

    elif operation == 'exportall':
        exportAll(GPG_CMD)

    else:
        printUsage()
