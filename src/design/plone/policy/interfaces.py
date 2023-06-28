# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IDesignPlonePolicyLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IDesignPlonePolicySettings(Interface):
    """IDesignPlonePolicySettings interface"""
