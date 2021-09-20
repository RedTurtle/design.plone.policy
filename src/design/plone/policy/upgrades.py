# -*- coding: utf-8 -*-
from copy import deepcopy
from design.plone.policy.interfaces import IDesignPlonePolicySettings
from design.plone.policy.setuphandlers import disable_searchable_types
from design.plone.policy.setuphandlers import set_default_subsite_colors
from plone import api
from plone.app.upgrade.utils import installOrReinstallProduct
from Products.CMFPlone.interfaces import ISelectableConstrainTypes

import logging


logger = logging.getLogger(__name__)

DEFAULT_PROFILE = "profile-design.plone.policy:default"


def update_profile(context, profile, run_dependencies=True):
    context.runImportStepFromProfile(DEFAULT_PROFILE, profile, run_dependencies)


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
        """ """
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
    brains = api.content.find(object_provides="plone.restapi.behaviors.IBlocks")
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


def to_1400(context):
    old = api.portal.get_registry_record(name="design.plone.policy.twitter_token")
    context.runAllImportStepsFromProfile("profile-design.plone.policy:to_1400")
    update_registry(context)

    if old:
        api.portal.set_registry_record(
            "twitter_token", old, interface=IDesignPlonePolicySettings
        )


def to_1500(context):
    """This upgrade handles that a type "Bando" is now  addmitted by default
    inside the folder "Documenti e Dati".
    This method just ADD THE CONTENT TYPE to the current list of types that you
    can add inside that folder only if it's not already there.
    tp#17807
    """

    doc_brains = api.content.find(portal_type="Document")
    doc_e_dati_list = [x for x in doc_brains if x.Title == "Documenti e dati"]
    if len(doc_e_dati_list) == 1:
        doc_e_dati = doc_e_dati_list[0].getObject()

        constraints = ISelectableConstrainTypes(doc_e_dati)
        allowed_types = constraints.getLocallyAllowedTypes()
        if "Bando" not in allowed_types:
            allowed_types.append("Bando")
            constraints.setLocallyAllowedTypes(allowed_types)

            logger.info("Enabled 'Bando' inside 'Ducumenti e dati' folder.")
        else:
            logger.info(
                "'Bando' already enabled in 'Ducumenti e dati' folder,"
                " not changes needed."
            )
    else:
        logger.warning(
            "More than one Document with title 'Documenti e dati'. "
            "Type 'Bando' inside 'Ducumenti e dati' folder not "
            "enabled."
        )


def to_1600(context):
    installOrReinstallProduct(api.portal.get(), "collective.volto.subsites")
    set_default_subsite_colors()
    logger.info("### CHANGE SUBSITE COLOR light-blue => teal")
    subsites = api.content.find(portal_type="Subsite")
    for brain in subsites:
        subsite = brain.getObject()
        if getattr(subsite, "subsite_css_class", "") == "light-blue":
            subsite.subsite_css_class = "teal"
            logger.info("- {}".format(brain.getURL()))


def to_1700(context):
    installOrReinstallProduct(api.portal.get(), "collective.volto.subfooter")
