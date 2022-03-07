# -*- coding: utf-8 -*-
"""Init and utils."""
from zope.i18nmessageid import MessageFactory
from .sensitive import apply

_ = MessageFactory("design.plone.policy")
apply()
