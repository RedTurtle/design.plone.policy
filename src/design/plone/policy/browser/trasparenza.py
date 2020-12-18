from Products.Five.browser import BrowserView
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from zope.component import queryUtility
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from design.plone.policy.browser.config import STRUTTURA
from uuid import uuid4

import logging

logger = logging.getLogger("trasparenza")


def set_property(context, prop_name, value):
    if context.hasProperty(prop_name):
        context.manage_changeProperties(prop_name=value)
    else:
        context.manage_addProperty(prop_name, value, 'string')


def setAllowedContents(content, allowed_ct):
    content.setConstrainTypesMode(1)
    content.setLocallyAllowedTypes(allowed_ct)
    content.setImmediatelyAddableTypes(allowed_ct)


def set_layout(context, layout_name):
    if context.hasProperty('default_page'):
        context.manage_delProperties(['default_page'])
    set_property(context, 'layout', layout_name)


class CreaTrasparenza(BrowserView):
    def __call__(self):
        parent = self.context
        try:
            children = self.context.struttura_trasparenza()
        except Exception:
            children = STRUTTURA
        alsoProvides(self.request, IDisableCSRFProtection)
        _createObjects(parent, children)


def _createObjects(parent, children):

    wftool = getToolByName(parent, "portal_workflow")

    for new_obj in children:
        logger.info("Processing object: %s" % new_obj['id'])

        #            if new_obj.get('lang', '') == 'neutral':
        #                language = ''
        #            else:
        #                language = 'it'

        local_parent = parent
        existing = parent.objectIds()
        new_obj['id'] = queryUtility(IURLNormalizer).normalize(new_obj['id'])
        if 'remove' in new_obj:
            logger.info("Removing content: %s" % new_obj['id'])
            if new_obj['id'] in existing:
                local_parent.manage_delObjects(
                    [
                        new_obj['id'],
                    ]
                )
            else:
                logger.info("Content to be removed does not exists: %s" % new_obj['id'])
            continue
        elif new_obj['id'] not in existing:
            _createObjectByType(
                new_obj['type'],
                local_parent,
                id=new_obj['id'],
                title=new_obj.get('title', ''),
                description=new_obj.get('description', ''),
            )
            logger.info("Creating content: %s" % new_obj['id'])

        else:
            logger.info("%s already exists" % new_obj['id'])
        logger.info("Now to modify the new_obj...")
        obj = local_parent.get(new_obj['id'], None)
        if obj is None:
            logger.info("can't get new_obj %s to modify it!" % new_obj['id'])
            continue
        #            obj.setLanguage(language)
        if obj.portal_type != new_obj['type']:
            logger.error("types don't match!")
            continue
        if 'layout' in new_obj:
            set_layout(obj, new_obj['layout'])
        if 'workflow_transition' in new_obj:
            try:
                wftool.doActionFor(obj, new_obj['workflow_transition'])
            except WorkflowException:
                logger.warning("couldn't do workflow transition")
        # if 'exclude_from_nav' in new_obj:
        #     obj.setExcludeFromNav(new_obj['exclude_from_nav'])
        if 'allowed_types' in new_obj:
            setAllowedContents(obj, new_obj['allowed_types'])

        data = generate_listing_query(obj)
        obj.blocks = data['blocks']
        obj.blocks_layout = data['blocks_layout']

        obj.reindexObject()
        #            if language == 'it':
        #                kwargs = {}
        #                title = new_obj.get('en_title', None)
        #                if title:
        #                    kwargs['title'] = title
        #                _id = new_obj.get('en_id', None)
        #                if _id:
        #                    kwargs['id'] = _id
        #                try:
        #                    obj.addTranslation('en', **kwargs)
        #                except (AlreadyTranslated, BadRequest):
        #                    pass

        children = new_obj.get('children', [])
        if len(children) > 0:
            _createObjects(obj, children)
        # this needs to be done after children creation
        if 'default_page' in new_obj and new_obj['default_page'] in obj.objectIds():
            obj.setDefaultPage(new_obj['default_page'])


def generate_listing_query(obj):
    title_uuid = str(uuid4())
    listing_uuid = str(uuid4())
    data = {}
    query = [
        {
            "i": "path",
            "o": "plone.app.querystring.operation.string.path",
            "v": "{uid}::1".format(uid=getattr(obj, '_plone.uuid')),
        }
    ]
    data["blocks"] = {
        title_uuid: {"@type": "title"},
        listing_uuid: {
            "@type": "listing",
            "query": query,
            "sort_on": obj.get("sort_on", "getObjPositionInParent"),
            "sort_order": obj.get("sort_reversed", False),
            "b_size": obj.get("item_count", "30"),
            "block": listing_uuid,
        },
    }
    data["blocks_layout"] = {"items": [title_uuid, listing_uuid]}
    return data
