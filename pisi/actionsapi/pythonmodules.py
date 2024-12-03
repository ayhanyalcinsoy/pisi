# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2010 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

# Standard Python modules
import os
import glob
import gettext

# Gettext setup
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.gettext

# Pisi Modules
import pisi.context as ctx

# ActionsAPI Modules
import pisi.actionsapi
import pisi.actionsapi.get as get
from pisi.actionsapi.shelltools import system, can_access_file, unlink, isEmpty
from pisi.actionsapi.pisitools import dodoc


# Custom error classes
class ConfigureError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        super().__init__(value)
        ctx.ui.error(value)


class CompileError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        super().__init__(value)
        ctx.ui.error(value)


class InstallError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        super().__init__(value)
        ctx.ui.error(value)


class RunTimeError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        super().__init__(value)
        ctx.ui.error(value)


# Functions
def configure(parameters='', pyVer='3'):
    """Runs python setup.py configure."""
    if system(f'python{pyVer} -m build --wheel --no-isolation configure {parameters}'):
        raise ConfigureError(_('Configuration failed.'))


def compile(parameters='', pyVer='3'):
    """Compiles source with the given parameters."""
    if system(f'python{pyVer} -m build --wheel --no-isolation {parameters}'):
        raise CompileError(_('Make failed.'))


def install(parameters='', pyVer='3'):
    """Installs the built package."""
    if system(f'python{pyVer} -m installer --destdir={get.installDIR()} dist/*.whl {parameters}'):
        raise InstallError(_('Install failed.'))

    # Handle documentation files
    docFiles = (
        'AUTHORS', 'CHANGELOG', 'CONTRIBUTORS', 'COPYING*', 'COPYRIGHT',
        'Change*', 'KNOWN_BUGS', 'LICENSE', 'MAINTAINERS', 'NEWS',
        'README*', 'PKG-INFO'
    )

    for docGlob in docFiles:
        for doc in glob.glob(docGlob):
            if not isEmpty(doc):
                dodoc(doc)


def run(parameters='', pyVer='3'):
    """Executes the given parameters with Python."""
    if system(f'python{pyVer} {parameters}'):
        raise RunTimeError(_('Running %s failed.') % parameters)


def fixCompiledPy(lookInto=f'/usr/lib/{get.curPYTHON()}/'):
    """Removes .py[co] files from packages."""
    install_dir = get.installDIR()
    for root, dirs, files in os.walk(f'{install_dir}/{lookInto}'):
        for compiledFile in files:
            if compiledFile.endswith('.pyc') or compiledFile.endswith('.pyo'):
                file_path = os.path.join(root, compiledFile)
                if can_access_file(file_path):
                    unlink(file_path)
