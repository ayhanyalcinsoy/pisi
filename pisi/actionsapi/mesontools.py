# -*- coding: utf-8 -*-
import gettext

import pisi.actionsapi
import pisi.context as ctx
from pisi.actionsapi import get
from pisi.actionsapi.shelltools import system

# gettext setup
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.gettext


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


# Functions
def configure(parameters='', build_dir='build'):
    """
    Configures the project into the build directory with the parameters using meson.

    Args:
        parameters (str): Extra parameters for the command. Default is an empty string.
        build_dir (str): Build directory. Default is 'build'.

    Examples:
        >>> mesontools.configure()
        >>> mesontools.configure('extra parameters')
        >>> mesontools.configure('extra parameters', 'custom_build_dir')
    """
    default_parameters = ' '.join([
        '--prefix=/%s' % get.defaultprefixDIR(),
        '--bindir=/usr/bin',
        '--datadir=/%s' % get.dataDIR(),
        '--includedir=/usr/include',
        '--infodir=/%s' % get.infoDIR(),
        '--libdir=/%s' % ('usr/lib32' if get.buildTYPE() == 'emul32' else 'usr/lib'),
        '--libexecdir=/%s' % get.libexecDIR(),
        '--localedir=/usr/share/locale',
        '--localstatedir=/%s' % get.localstateDIR(),
        '--mandir=/%s' % get.manDIR(),
        '--sbindir=/%s' % get.sbinDIR(),
        '--sharedstatedir=com',
        '--sysconfdir=/etc',
        '--default-library=shared',
    ])
    if system(f'meson setup {default_parameters} {parameters} {build_dir}'):
        raise ConfigureError(_('Configuration failed.'))


def build(parameters='', build_dir='build'):
    """
    Builds the project into the build directory with the parameters using ninja.

    Args:
        parameters (str): Extra parameters for the command. Default is an empty string.
        build_dir (str): Build directory. Default is 'build'.

    Examples:
        >>> mesontools.build()
        >>> mesontools.build('extra parameters')
        >>> mesontools.build('extra parameters', 'custom_build_dir')
    """
    if system(f'ninja -C {build_dir} {parameters} {get.makeJOBS()}'):
        raise CompileError(_('Make failed.'))


def install(parameters='', build_dir='build'):
    """
    Installs the project to the destination directory.

    Args:
        parameters (str): Extra parameters for the command. Default is an empty string.
        build_dir (str): Build directory. Default is 'build'.

    Examples:
        >>> mesontools.install()
        >>> mesontools.install('extra parameters')
        >>> mesontools.install('extra parameters', 'custom_build_dir')
    """
    if system(f'DESTDIR={get.installDIR()} ninja -C {build_dir} {parameters} install'):
        raise InstallError(_('Install failed.'))
