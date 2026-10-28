from operator import itemgetter
from plone.app.vocabularies.language import (
    AvailableContentLanguageVocabulary,
    SupportedContentLanguageVocabulary,
)
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


def _label(code, name):
    return f"{name} ({code})"


class AvailableContentLanguageWithCodeVocabulary(AvailableContentLanguageVocabulary):
    """Like the Plone one, but the label also contains the language code."""

    def __call__(self, context):
        items = [SimpleTerm("en", "en", _label("en", "English"))]
        ltool = getToolByName(getSite(), "portal_languages", None)
        if ltool is not None:
            languages = ltool.getAvailableLanguages()
            items = [
                (lang, _label(lang, languages[lang].get("native", lang)))
                for lang in languages
            ]
            items.sort(key=itemgetter(1))
            items = [SimpleTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(items)


class SupportedContentLanguageWithCodeVocabulary(SupportedContentLanguageVocabulary):
    """Like the Plone one, but the label also contains the language code."""

    def __call__(self, context):
        items = []
        ltool = getToolByName(getSite(), "portal_languages", None)
        if ltool is not None:
            all_langs = ltool.getAvailableLanguages()
            items = [
                (
                    lang[0],
                    _label(lang[0], all_langs.get(lang[0], {}).get("native", lang[1])),
                )
                for lang in ltool.listSupportedLanguages()
            ]
            items.sort(key=itemgetter(1))
            items = [SimpleTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(items)


AvailableContentLanguageWithCodeVocabularyFactory = (
    AvailableContentLanguageWithCodeVocabulary()
)
SupportedContentLanguageWithCodeVocabularyFactory = (
    SupportedContentLanguageWithCodeVocabulary()
)
