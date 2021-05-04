# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from zope import schema


class IDesignPlonePolicyLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IDesignPlonePolicySettings(Interface):

    twitter_token = schema.TextLine(title=u"Twitter Bearer token")
