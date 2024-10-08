# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Global variables here

import signal

import pisi.constants
import pisi.signalhandler
import pisi.ui

const = pisi.constants.Constants()
sig = pisi.signalhandler.SignalHandler()

config = None

log = None

# Used for bug #10568
locked = False

def set_option(opt, val):
    if config:  # Ensure config is not None before calling
        config.set_option(opt, val)

def get_option(opt):
    return config.get_option(opt) if config else None

ui = pisi.ui.UI()

# stdout, stderr for PiSi API
stdout = None
stderr = None

comar = True
comar_updated = False
dbus_sockname = None
dbus_timeout = 60 * 60  # In seconds

# Bug #2879
# FIXME: Maybe we can create a simple rollback mechanism. There are other
# places which need this, too.
# This is needed in build process to clean up if something goes wrong.
build_leftover = None

def disable_keyboard_interrupts():
    if sig:  # Ensure sig is not None before calling
        sig.disable_signal(signal.SIGINT)

def enable_keyboard_interrupts():
    if sig:  # Ensure sig is not None before calling
        sig.enable_signal(signal.SIGINT)

def keyboard_interrupt_disabled():
    return sig and sig.signal_disabled(signal.SIGINT)

def keyboard_interrupt_pending():
    return sig and sig.signal_pending(signal.SIGINT)

filesdb = None
