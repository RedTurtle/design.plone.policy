# -*- coding: utf-8 -*-
"""Helpers shared by the upgrade steps."""

from Acquisition import aq_base
from collective.volto.blocksfield.field import BlocksField
from copy import deepcopy
from design.plone.policy.upgrades import logger
from plone import api
from plone.dexterity.utils import iterSchemata
from zope.schema import getFields


def process_blocks_fields(obj, func):
    """Apply func to the blocks and blocks fields of obj.

    ``func(context, blocks)`` changes the blocks in place and returns a list of
    stats, with an "error" key for the blocks it could not process. A field is
    saved only if it has at least one change without errors.
    """
    item = aq_base(obj)
    changes = []
    names = {"blocks"}
    for schema in iterSchemata(item):
        for name, field in getFields(schema).items():
            if isinstance(field, BlocksField):
                names.add(name)
    for name in sorted(names):
        value = getattr(item, name, None)
        if not value or not isinstance(value, dict):
            continue
        value = deepcopy(value)
        # the "blocks" field is the blocks dict, a BlocksField wraps it
        blocks = value if name == "blocks" else value.get("blocks")
        field_changes = func(obj, blocks)
        if any("error" not in stats for stats in field_changes):
            setattr(item, name, value)
        changes.extend(field_changes)
    return changes


def iter_blocks_candidates(block_types, prefix):
    """Yield ``(path, get_object)`` for the site root and the contents that
    may have blocks of the given types."""
    portal = api.portal.get()
    catalog = api.portal.get_tool("portal_catalog")

    # block_types also covers the blocks fields (collective.volto.blocksfield)
    if "block_types" in catalog.indexes():
        brains = list(catalog.unrestrictedSearchResults(block_types=list(block_types)))
    else:
        brains = list(catalog.getAllBrains())

    seen = set()
    candidates = [("/".join(portal.getPhysicalPath()), lambda: portal)]
    candidates += [(b.getPath(), b._unrestrictedGetObject) for b in brains]
    tot = len(candidates)
    for i, (path, get_object) in enumerate(candidates):
        if path in seen:
            continue
        seen.add(path)
        if i and i % 1000 == 0:
            logger.info(f"{prefix} Progress: {i}/{tot}")
            portal._p_jar.cacheGC()
        yield path, get_object
