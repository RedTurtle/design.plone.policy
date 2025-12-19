# -*- coding: utf-8 -*-
"""Init and utils."""
from .sensitive import apply
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("design.plone.policy")
apply()
