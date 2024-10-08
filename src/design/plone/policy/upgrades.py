# -*- coding: utf-8 -*-
from Acquisition import aq_base
from collective.volto.blocksfield.field import BlocksField
from copy import deepcopy
from design.plone.policy.interfaces import IDesignPlonePolicySettings
from design.plone.policy.setuphandlers import disable_searchable_types
from design.plone.policy.setuphandlers import set_default_subsite_colors
from design.plone.policy.utils import create_default_blocks
from plone import api
from plone.app.upgrade.utils import installOrReinstallProduct
from plone.dexterity.utils import iterSchemata
from plone.registry.interfaces import IRegistry
from plone.restapi.behaviors import IBlocks
from Products.CMFPlone.interfaces import IFilterSchema
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from zope.component import getUtility
from zope.schema import getFields

import json
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


def to_1800(context):
    installOrReinstallProduct(api.portal.get(), "rer.customersatisfaction")


def to_1900(context):
    installOrReinstallProduct(api.portal.get(), "redturtle.faq")


def to_1910(context):
    allowed_sizes = api.portal.get_registry_record("plone.allowed_sizes")
    new_sizes = []
    skip = ["listing 16:16", "icon 32:32", "tile 64:64"]
    for size in allowed_sizes:
        if size in skip:
            new_sizes.append(size)
        else:
            name_height, width = size.split(":")
            if width != "65536":
                new_sizes.append("{}:{}".format(name_height, "65536"))
            else:
                new_sizes.append(size)
    if "midi 300:65536" not in new_sizes:
        new_sizes.insert(new_sizes.index("mini 200:65536") + 1, "midi 300:65536")
    api.portal.set_registry_record("plone.allowed_sizes", new_sizes)


def to_2000(context):  # noqa: C901
    logger.info("### START CONVERSION FORMS: enable honeypot ###")

    def fix_block(blocks):
        found = False
        for block in blocks.values():
            if block.get("@type", "") == "form":
                captcha = block.get("captcha", "")
                if captcha != "honeypot":
                    block["captcha"] = "honeypot"
                    found = True
        return found

    forms = []

    # fix root
    portal = api.portal.get()
    try:
        portal_blocks = json.loads(portal.blocks)
        res = fix_block(portal_blocks)
        if res:
            forms.append("site root")
            portal.blocks = json.dumps(portal_blocks)
    except TypeError:
        # This happens when the site was already Plone 6
        # and the blocks field is already a dictionary.
        # Since it's Plone 6, the site root will be in the catalog query below,
        # so just skip this step.
        pass

    # fix blocks in contents
    pc = api.portal.get_tool(name="portal_catalog")
    brains = pc()
    tot = len(brains)
    i = 0
    for brain in brains:
        i += 1
        if i % 1000 == 0:
            logger.info("Progress: {}/{}".format(i, tot))
        item = aq_base(brain.getObject())
        for schema in iterSchemata(item):
            for name, field in getFields(schema).items():
                if name == "blocks":
                    blocks = deepcopy(item.blocks)
                    if blocks:
                        res = fix_block(blocks)
                        if res:
                            forms.append(brain.getURL())
                            item.blocks = blocks
                elif isinstance(field, BlocksField):
                    value = deepcopy(field.get(item))
                    if not value:
                        continue
                    try:
                        blocks = value.get("blocks", {})
                    except AttributeError:
                        logger.warning(
                            "[RICHTEXT] - {} (not converted)".format(brain.getURL())
                        )
                    if blocks:
                        res = fix_block(blocks)
                        if res:
                            forms.append(brain.getURL())
                            setattr(item, name, value)

    logger.info(f"Found {len(forms)} forms.")
    for url in forms:
        logger.info(f"- {url}")


def to_2010(context):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IFilterSchema, prefix="plone")
    settings.custom_attributes = settings.custom_attributes + ["data-element"]


def update_folders(context, CHANGES=[], NEW_ITEMS=[]):
    GREEN = "\033[92m"
    ENDC = "\033[0m"
    RED = "\033[91m"

    portal = api.portal.get()
    portal_name = portal.getId()
    for item in CHANGES:
        try:
            folder = portal.restrictedTraverse("{}{}".format(portal_name, item))
            old_title = folder.title
            old_path = "/".join(folder.getPhysicalPath())
            api.content.rename(obj=folder, new_id=CHANGES[item][1])
            folder.title = CHANGES[item][0]
            # folder.reindexObject(idx=['id', 'title', 'getId', 'SearchableText'])
            # Who know the exact number of index we need to update?
            folder.reindexObject()
            logger.info(
                "{} Modificato {} ({}) in {} {}".format(
                    GREEN, old_title, old_path, folder.title, ENDC
                )
            )
        except KeyError:
            logger.info("{} Impossibile modificare {}{}".format(RED, item, ENDC))

    for item in NEW_ITEMS:
        folder = portal.restrictedTraverse("{}{}".format(portal_name, item[0]))
        if item[2] not in folder:
            new = api.content.create(
                type="Document", id=item[2], title=item[1], container=folder
            )
            logger.info(
                "{} Creato {} in {} {}".format(
                    GREEN, item[1], "/".join(new.getPhysicalPath()), ENDC
                )
            )
        else:
            logger.info(
                "{} {} esiste già in {} {}".format(
                    RED, item[1], "/".join(folder.getPhysicalPath()), ENDC
                )
            )


def update_folders_name_for_pnrr(context):
    CHANGES = {
        "/servizi/tributi-e-finanze": (
            "Tributi, finanze e contravvenzioni",
            "tributi-finanze-e-contravvenzioni",
        ),
        "/servizi/agricoltura": ("Agricoltura e pesca", "agricoltura-e-pesca"),
    }
    NEW_ITEMS = [
        ("/servizi", "Imprese e commercio", "imprese-e-commercio"),
    ]
    update_folders(context, CHANGES, NEW_ITEMS)


def to_3000(context):
    # run design.plone.contenttypes steps
    context.upgradeProfile(
        "profile-design.plone.contenttypes:default", dest="7001", quiet=False
    )
    update_folders_name_for_pnrr(context)


def to_3001(context):
    # run design.plone.contenttypes steps
    context.upgradeProfile(
        "profile-design.plone.contenttypes:default", dest="7008", quiet=False
    )
    context.runImportStepFromProfile(
        "profile-design.plone.contenttypes:default",
        "plone.app.registry",
        run_dependencies=False,
    )
    installOrReinstallProduct(api.portal.get(), "collective.feedback")


def to_3100(context):
    already_modified = []
    not_modified = []
    brains = api.content.find(object_provides=IBlocks.__identifier__)
    tot = len(brains)
    i = 0
    for brain in brains:
        i += 1
        if i % 1000 == 0:
            logger.info(f"Progress: {i}/{tot}")
        item = brain.getObject().aq_base
        blocks = getattr(item, "blocks", {})
        blocks_layout = getattr(item, "blocks_layout", {})

        if blocks and blocks_layout == {"items": []}:
            # case where document has been created without blocks, and has been modified
            item.blocks_layout = {"items": [x for x in blocks.keys()]}
            already_modified.append(brain.getPath())
            continue
        if not blocks and blocks_layout == {"items": []}:
            create_default_blocks(item)
            not_modified.append(brain.getPath())

    if already_modified:
        logger.info("### Items that were already modified ###")
        for i, path in enumerate(already_modified):
            logger.info(f"[{i+1}/{len(already_modified)}] - {path}")

    if not_modified:
        logger.info("### Items that were not modified ###")
        for i, path in enumerate(not_modified):
            logger.info(f"[{i+1}/{len(not_modified)}] - {path}")


def to_3101(context):
    for brain in api.portal.get_tool("portal_catalog")():
        item = aq_base(brain.getObject())

        for schema in iterSchemata(item):
            for name, field in getFields(schema).items():
                if name == "blocks":
                    logger.info(
                        f"[3100 - 3101] Deleting twitter blocks if "
                        f"exist from {'/'.join(item.getPhysicalPath())}"
                    )

                    twitter_block_uids = []
                    blocks = deepcopy(item.blocks)
                    blocks_layout = deepcopy(getattr(item, "blocks_layout", {}))

                    for key, block in deepcopy(blocks).items():
                        if block.get("@type", "") == "twitter_posts":
                            twitter_block_uids.append(key)
                            del blocks[key]

                    for block_uid in [*item.blocks_layout.get("items", [])]:
                        if block_uid in twitter_block_uids:
                            blocks_layout["items"].remove(block_uid)

                    item.blocks = blocks

                    if blocks_layout:
                        item.blocks_layout = blocks_layout

                elif isinstance(field, BlocksField):
                    value = deepcopy(field.get(item))
                    if not value:
                        continue
                    try:
                        blocks = value.get("blocks", {})

                    except AttributeError:
                        logger.warning(
                            "[BLOCK] - {} (not converted)".format(brain.getURL())
                        )

                    if blocks:
                        logger.info(
                            f"[3100 - 3101] Deleting twitter blocks if "
                            f"exist from {'/'.join(item.getPhysicalPath())}"
                        )

                        twitter_block_uids = []
                        blocks = deepcopy(getattr(item, "blocks", None))

                        blocks_layout = deepcopy(getattr(item, "blocks_layout", None))

                        if blocks and blocks_layout:
                            for key, block in deepcopy(blocks).items():
                                if block.get("@type", "") == "twitter_posts":
                                    twitter_block_uids.append(key)
                                    del blocks[key]

                            for block_uid in [*item.blocks_layout.get("items", [])]:
                                if block_uid in twitter_block_uids:
                                    blocks_layout["items"].remove(block_uid)

                            item.blocks = blocks

                            if blocks_layout:
                                item.blocks_layout = blocks_layout
