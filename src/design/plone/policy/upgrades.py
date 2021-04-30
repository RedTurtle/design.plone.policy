# -*- coding: utf-8 -*-
from copy import deepcopy
from design.plone.policy.setuphandlers import disable_searchable_types
from plone.app.upgrade.utils import installOrReinstallProduct
from plone import api

import logging


logger = logging.getLogger(__name__)

DEFAULT_PROFILE = "profile-design.plone.policy:default"


def update_profile(context, profile, run_dependencies=True):
    context.runImportStepFromProfile(
        DEFAULT_PROFILE, profile, run_dependencies
    )


def update_types(context):
    update_profile(context, "typeinfo")


def update_rolemap(context):
    update_profile(context, "rolemap")


def update_registry(context):
    update_profile(context, "plone.app.registry", run_dependencies=False)


def update_catalog(context):
    update_profile(context, "catalog")


def update_controlpanel(context):
    update_profile(context, "controlpanel")


def to_1200(context):
    def fix_field_name(blocks):
        """
        """
        found = False
        for block in blocks.values():
            if block.get("@type", "") == "form" and block.get("to", ""):
                block["default_to"] = block.get("to", "")
                del block["to"]
                found = True
        return found

    installOrReinstallProduct(api.portal.get(), "collective.volto.formsupport")
    logger.info("Changing form block fields.")
    i = 0
    brains = api.content.find(
        object_provides="plone.restapi.behaviors.IBlocks"
    )
    tot = len(brains)
    fixed_items = []
    for brain in brains:
        i += 1
        if i % 1000 == 0:
            logger.info("Progress: {}/{}".format(i, tot))
        item = brain.getObject()
        blocks = deepcopy(getattr(item, "blocks", {}))
        if blocks:
            to_update = fix_field_name(blocks)
            if to_update:
                item.blocks = blocks
                fixed_items.append(brain.getPath())

    logger.info("Finish")
    if fixed_items:
        logger.info("Updated items:")
        for fixed in fixed_items:
            logger.info("- {}".format(fixed))
    else:
        logger.info("No items affected.")


def to_1300(context):
    disable_searchable_types()
