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

# Standard Python Modules
import os
import gettext

__trans = gettext.translation('pisi', fallback=True)
_ = __trans.gettext  # Python 3'te ugettext yerine gettext kullanılır.

# Pisi-Core Modules
import pisi.context as ctx
from pisi.util import join_path

# ActionsAPI Modules
import pisi.actionsapi
from pisi.actionsapi.shelltools import *
import pisi.actionsapi.get as get

class RunTimeError(pisi.actionsapi.Error):
    def __init__(self, value=''):
        super().__init__(value)  # Python 3'te super() kullanımı
        self.value = value
        ctx.ui.error(value)

def preplib(sourceDirectory='/usr/lib'):
    sourceDirectory = join_path(get.installDIR(), sourceDirectory)
    if can_access_directory(sourceDirectory):
        if system('/sbin/ldconfig -n -N %s' % sourceDirectory):
            raise RunTimeError(_('Running ldconfig failed.'))

def gnuconfig_update():
    ''' copy newest config.* onto source's '''
    for root, dirs, files in os.walk(os.getcwd()):
        for fileName in files:
            if fileName in ['config.sub', 'config.guess']:
                targetFile = os.path.join(root, fileName)
                if os.path.islink(targetFile):
                    os.unlink(targetFile)  # unlink yerine os.unlink kullanıyoruz
                copy('/usr/share/gnuconfig/%s' % fileName, join_path(root, fileName))
                ctx.ui.info(_('GNU Config Update Finished.'))

def libtoolize(parameters=''):
    if system('/usr/bin/libtoolize %s' % parameters):
        raise RunTimeError(_('Running libtoolize failed.'))

def gen_usr_ldscript(dynamicLib):
    makedirs('%s/usr/lib' % get.installDIR())

    with open('%s/usr/lib/%s' % (get.installDIR(), dynamicLib), 'w') as destinationFile:  # Dosya açma işlemi için context manager kullanıyoruz.
        content = f'''
/* GNU ld script
    Since Pardus has critical dynamic libraries
    in /lib, and the static versions in /usr/lib,
    we need to have a "fake" dynamic lib in /usr/lib,
    otherwise we run into linking problems.
*/
GROUP ( /lib/{dynamicLib} )
'''
        destinationFile.write(content)

    chmod('%s/usr/lib/%s' % (get.installDIR(), dynamicLib))
