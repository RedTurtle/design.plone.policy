# -*- coding: utf-8 -*-
"""Init and utils."""

from .sensitive import apply
from zope.i18nmessageid import MessageFactory
from zope.i18n.interfaces import ITranslationDomain
from zope.component import queryUtility
import logging

logger = logging.getLogger(__name__)

_ = MessageFactory("design.plone.policy")
apply()


def initialize(context):
    """Be sure that we have our translations loaded before the othe ones
       Fix proposto da @alert dell'ordine delle traduzioni preso da
       https://community.plone.org/t/overriding-plone-app-locales/12021/14
    """
    translation_domain = queryUtility(ITranslationDomain, "plone")
    if not translation_domain:
        return

    for lang in translation_domain._catalogs:
        original = translation_domain._catalogs[lang]
        # This will enforce our translations to be at the top of the list
        tweaked = sorted(
            original, key=lambda path: "design/plone/policy/locales" not in path
        )
        if tweaked != original:
            logger.warning("Boosting this package translations")
            translation_domain._catalogs[lang] = tweaked
