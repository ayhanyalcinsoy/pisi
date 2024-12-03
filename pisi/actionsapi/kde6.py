# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

# ActionsAPI Modules
from pisi.actionsapi import get
from pisi.actionsapi import cmaketools
from pisi.actionsapi import shelltools

basename = "kde6"

prefix = f"/{get.defaultprefixDIR()}"
libdir = f"{prefix}/lib"
bindir = f"{prefix}/bin"
libexecdir = f"{prefix}/lib"
iconsdir = f"{prefix}/share/icons"
applicationsdir = f"{prefix}/share/applications/{basename}"
mandir = f"/{get.manDIR()}"
sharedir = f"{prefix}/share"
localedir = f"{prefix}/share/locale"
qmldir = f"{prefix}/lib/qt6/qml"
plugindir = f"{prefix}/lib/qt6/plugins"
moduledir = f"{prefix}/lib/qt6/mkspecs/modules"
pythondir = f"{prefix}/bin/python"
appsdir = f"{sharedir}"
sysconfdir = "/etc"
configdir = f"{sysconfdir}/xdg"
servicesdir = f"{sharedir}/services"
servicetypesdir = f"{sharedir}/servicetypes"
includedir = f"{prefix}/include"
docdir = f"/{get.docDIR()}/{basename}"
htmldir = f"{docdir}/html"
wallpapersdir = f"{prefix}/share/wallpapers"

def configure(parameters='', installPrefix=prefix, sourceDir='..'):
    """
    Configure the build system using CMake.

    Args:
        parameters (str): Additional CMake parameters.
        installPrefix (str): The installation prefix directory.
        sourceDir (str): The source directory for CMake configuration.

    Examples:
        >>> configure("-DSOME_OPTION=ON", "/usr", "../source")
    """
    shelltools.makedirs("build")
    shelltools.cd("build")

    cmaketools.configure(
        f"-DCMAKE_BUILD_TYPE=Release "
        f"-DKDE_INSTALL_LIBEXECDIR={libexecdir} "
        f"-DCMAKE_INSTALL_LIBDIR=lib "
        f"-DKDE_INSTALL_USE_QT_SYS_PATHS=ON "
        f"-DKDE_INSTALL_QMLDIR={qmldir} "
        f"-DKDE_INSTALL_SYSCONFDIR={sysconfdir} "
        f"-DKDE_INSTALL_PLUGINDIR={plugindir} "
        f"-DECM_MKSPECS_INSTALL_DIR={moduledir} "
        f"-DBUILD_TESTING=OFF "
        f"-DKDE_INSTALL_LIBDIR=lib "
        f"-DQT_MAJOR_VERSION=6 "
        f"-Wno-dev "
        f"-DCMAKE_INSTALL_PREFIX={prefix} {parameters}",
        installPrefix,
        sourceDir
    )

    shelltools.cd("..")


def make(parameters=''):
    """
    Build the project using CMake.

    Args:
        parameters (str): Additional build parameters.

    Examples:
        >>> make("-j4")
    """
    cmaketools.make(f'-C build {parameters}')


def install(parameters='', argument='install'):
    """
    Install the project using CMake.

    Args:
        parameters (str): Additional installation parameters.
        argument (str): The installation argument (e.g., "install" or "package").

    Examples:
        >>> install("-DCOMPONENT=runtime")
    """
    cmaketools.install(f'-C build {parameters}', argument)
