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

"""
xmlext is a helper module for accessing XML files using
xml.dom.minidom. It is a convenient wrapper for some
DOM functions, and provides path based get/add functions
as in KDE API.

Function names are mixedCase for compatibility with minidom,
an 'old library'.

This implementation uses piksemel.
"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import piksemel as iks

parse = iks.parse
newDocument = iks.newDocument

def getAllNodes(node, tagPath):
    """Retrieve all nodes that match a given tag path."""
    tags = tagPath.split('/')
    if len(tags) == 0:
        return []
    nodeList = [node]  # basis case
    for tag in tags:
        results = [getTagByName(x, tag) for x in nodeList]
        nodeList = []
        for x in results:
            nodeList.extend(x)
        if len(nodeList) == 0:
            return []
    return nodeList

def getNodeAttribute(node, attrname):
    """Get named attribute from DOM node."""
    return node.getAttribute(attrname)

def setNodeAttribute(node, attrname, value):
    """Set named attribute for DOM node."""
    return node.setAttribute(attrname, value)

def getChildElts(parent):
    """Get only child elements."""
    return [x for x in parent.tags()]

def getTagByName(parent, childName):
    return [x for x in parent.tags(childName)]

def getNodeText(node, tagpath=""):
    """Get the first child and expect it to be text!"""
    if tagpath != "":
        node = getNode(node, tagpath)
        if not node:
            return None
    child = node.firstChild()
    if not child:
        return None
    if child.type() == iks.DATA:
        # In any case, strip whitespaces...
        return child.data().strip()
    else:
        raise XmlError(_("getNodeText: Expected text node, got something else!"))

def getChildText(node_s, tagpath):
    """Get the text of a child at the end of a tag path."""
    node = getNode(node_s, tagpath)
    if not node:
        return None
    return getNodeText(node)

def getNode(node, tagpath):
    """Returns the *first* matching node for given tag path."""
    if tagpath == "":
        return node

    assert isinstance(tagpath, str)
    tags = tagpath.split('/')
    assert len(tags) > 0

    # Iterative code to search for the path
    for tag in tags:
        currentNode = None
        for child in node.tags():
            if child.name() == tag:
                currentNode = child
                break
        if not currentNode:
            return None
        else:
            node = currentNode
    return currentNode

def createTagPath(node, tags):
    """Create new child at the end of a tag chain starting from node no matter what."""
    if len(tags) == 0:
        return node
    for tag in tags:
        node = node.insertTag(tag)
    return node

def addTagPath(node, tags, newnode=None):
    """Add newnode at the end of a tag chain, smart one."""
    node = createTagPath(node, tags)
    if newnode:  # Node to add specified
        node.insertNode(newnode)
    return node

def addNode(node, tagpath, newnode=None, branch=True):
    """Add a new node at the end of the tree and returns it. 
    If newnode is given adds that node, too."""

    assert isinstance(tagpath, str)
    tags = []
    if tagpath != "":
        tags = tagpath.split('/')  # tag chain
    else:
        addTagPath(node, [], newnode)
        return node  # FIXME: is this correct!?!?

    assert len(tags) > 0  # We want a chain

    # Iterative code to search for the path
    rem = 1 if branch else 0

    while len(tags) > rem:
        tag = tags.pop(0)
        nodeList = getTagByName(node, tag)
        if len(nodeList) == 0:  # Couldn't find
            tags.insert(0, tag)  # Put it back in
            return addTagPath(node, tags, newnode)
        else:
            node = nodeList[-1]  # Discard other matches
    else:
        # Had only one tag...
        return addTagPath(node, tags, newnode)

    return node

def addText(node, tagpath, text):
    node = addNode(node, tagpath)
    node.insertData(text)

def newNode(node, tag):
    return iks.newDocument(tag)
