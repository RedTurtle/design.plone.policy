# -*- coding: utf-8 -*-
from iw.rejectanonymous import rejectAnonymous


def insertRejectAnonymousHook(portal, event):
    """force authentication for request with X-ForceAuth header"""
    if event.request.getHeader("X-ForceAuth"):
        event.request.post_traverse(rejectAnonymous, (portal, event.request))
