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
import re
import sys
from itertools import zip, map, count, filterfalse, filter

# ActionsAPI
import pisi.actionsapi

def cat(filename):
    with open(filename) as f:
        return f.readlines()

class grep:
    '''Keep only lines that match the regexp.'''
    def __init__(self, pat, flags=0):
        self.fun = re.compile(pat, flags).match
        
    def __ror__(self, input):
        return filter(self.fun, input)

class tr:
    '''Apply arbitrary transform to each sequence element.'''
    def __init__(self, transform):
        self.tr = transform
        
    def __ror__(self, input):
        return map(self.tr, input)

class printto:
    '''Print sequence elements one per line.'''
    def __init__(self, out=sys.stdout):
        self.out = out
        
    def __ror__(self, input):
        for line in input:
            print(line, file=self.out)

printlines = printto(sys.stdout)

class terminator:
    def __init__(self, method):
        self.process = method
        
    def __ror__(self, input):
        return self.process(input)

aslist = terminator(list)
asdict = terminator(dict)
astuple = terminator(tuple)
join = terminator(''.join)
enum = terminator(enumerate)

class sort:
    def __ror__(self, input):
        ll = list(input)
        ll.sort()
        return ll

sort = sort()

class uniq:
    def __ror__(self, input):
        prev = None
        for i in input:
            if i == prev:
                continue
            prev = i
            yield i

uniq = uniq()
