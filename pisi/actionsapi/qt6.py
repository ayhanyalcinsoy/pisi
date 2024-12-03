# -*- coding: utf-8 -*-

import os
import gettext

import pisi.actionsapi
import pisi.context as ctx
from pisi.actionsapi import get
from pisi.actionsapi.shelltools import system

__trans = gettext.translation('pisi', fallback=True)
_ = __trans.gettext


class ConfigureError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        super().__init__(value)
        self.value = value
        ctx.ui.error(value)


class CompileError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        super().__init__(value)
        self.value = value
        ctx.ui.error(value)


class InstallError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        super().__init__(value)
        self.value = value
        ctx.ui.error(value)


basename = "qt6"

prefix = f"/{get.defaultprefixDIR()}"
libdir = f"{prefix}/lib"
bindirQt6 = f"{libdir}/{basename}"
libexecdir = f"{prefix}/libexec"
sysconfdir = "/etc"
bindir = f"{prefix}/bin"
includedir = f"{prefix}/include"

# qt5 specific variables

headerdir = f"{prefix}/include/{basename}"
datadir = f"{prefix}/share/{basename}"
docdir = f"/{get.docDIR()}/{basename}"
archdatadir = f"{libdir}/{basename}"
mkspecsdir = f"{libdir}/{basename}/mkspecs"
examplesdir = f"{libdir}/{basename}/examples"
testdir = f"{prefix}/share/{basename}"
translationdir = f"{datadir}/translations"

# Temporary bindir to avoid qt5 conflicts
qmake = f"{bindir}/qmake-qt6"


def configure(parameters='', build_dir='build'):
    """
    Configures the project into the build directory with the parameters using meson.

    Args:
        parameters (str): Extra parameters for the command. Default is empty string.
        build_dir (str): Build directory. Default is 'build'.

    Examples:
        >>> mesontools.configure()
        >>> mesontools.configure('extra parameters')
        >>> mesontools.configure('extra parameters', 'custom_build_dir')
    """
    default_parameters = ' '.join([
        f'-DCMAKE_INSTALL_PREFIX={prefix}',
        f'-DCMAKE_C_FLAGS="{get.CFLAGS()}"',
        f'-DCMAKE_CXX_FLAGS="{get.CXXFLAGS()}"',
        f'-DCMAKE_LD_FLAGS="{get.LDFLAGS()}"',
        '-DCMAKE_BUILD_TYPE=RelWithDebInfo',
        f'-DINSTALL_BINDIR={bindirQt6}',
        f'-DINSTALL_INCLUDEDIR={headerdir}',
        f'-DINSTALL_ARCHDATADIR={archdatadir}',
        f'-DINSTALL_DOCDIR={docdir}',
        f'-DINSTALL_DATADIR={datadir}',
        f'-DINSTALL_MKSPECSDIR={mkspecsdir}',
        f'-DINSTALL_EXAMPLESDIR={examplesdir}',
        '-DQT_FEATURE_libproxy=ON',
        '-DQT_FEATURE_vulkan=ON',
        '-DQT_FEATURE_system_freetype=ON',
        '-DQT_FEATURE_system_harfbuzz=ON',
        '-DQT_FEATURE_system_sqlite=ON',
        '-DQT_FEATURE_dbus_linked=ON',
        '-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON',
        '-DCMAKE_MESSAGE_LOG_LEVEL=STATUS',
        '-DQT_FEATURE_openssl_linked=ON',
    ])
    if system(f'cmake -B {build_dir} -G Ninja {default_parameters} {parameters}'):
        raise ConfigureError(_('Configuration failed.'))


def make(parameters='', build_dir='build'):
    """
    Builds the project into the build directory with the parameters using ninja. Instead of letting ninja
    to detect number of cores, this function gets the number from PISI configurations.

    Args:
        parameters (str): Extra parameters for the command. Default is empty string.
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
        parameters (str): Extra parameters for the command. Default is empty string.
        build_dir (str): Build directory. Default is 'build'.

    Examples:
        >>> mesontools.install()
        >>> mesontools.install('extra parameters')
        >>> mesontools.install('extra parameters', 'custom_build_dir')
    """
    if system(f'DESTDIR={get.installDIR()} ninja -C {build_dir} {parameters} install'):
        raise InstallError(_('Install failed.'))
