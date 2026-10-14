# -*- coding: utf-8 -*-
"""Dry run of the "optimize block images" upgrade step.

List the pages that the upgrade step would modify, without changing anything.

Usage (the Plone site id can be given as first argument, default "Plone"):

    bin/instance run scripts/dry_run_block_images.py [site_id]

Works on a copy of the blocks and never commits.
"""

from Acquisition import aq_base
from collective.volto.blocksfield.field import BlocksField
from copy import deepcopy
from design.plone.policy.block_images import BLOCK_TYPES
from design.plone.policy.block_images import format_change
from design.plone.policy.block_images import human_size
from design.plone.policy.block_images import optimize_blocks
from plone.dexterity.utils import iterSchemata
from zope.component.hooks import setSite
from zope.schema import getFields

import sys
import transaction


def block_field_names(item):
    names = {"blocks"}
    for schema in iterSchemata(item):
        for name, field in getFields(schema).items():
            if isinstance(field, BlocksField):
                names.add(name)
    return sorted(names)


def analyze(obj):
    """Return the changes the upgrade step would make on obj."""
    item = aq_base(obj)
    changes = []
    for name in block_field_names(item):
        value = getattr(item, name, None)
        if not value or not isinstance(value, dict):
            continue
        value = deepcopy(value)  # never touch the real data
        blocks = value if name == "blocks" else value.get("blocks")
        changes.extend(optimize_blocks(obj, blocks))
    return changes


def main():
    site_id = "Plone"
    if len(sys.argv) > 1 and not sys.argv[-1].endswith(".py"):
        site_id = sys.argv[-1]
    portal = app[site_id]  # noqa: F821 (provided by bin/instance run)
    setSite(portal)
    catalog = portal.portal_catalog

    if "block_types" in catalog.indexes():
        brains = list(catalog.unrestrictedSearchResults(block_types=list(BLOCK_TYPES)))
    else:
        brains = list(catalog.unrestrictedSearchResults())

    candidates = [("/".join(portal.getPhysicalPath()), lambda: portal)]
    candidates += [(b.getPath(), b._unrestrictedGetObject) for b in brains]

    seen = set()
    pages = []
    errors = []
    for i, (path, get_object) in enumerate(candidates):
        if path in seen:
            continue
        seen.add(path)
        if i and i % 1000 == 0:
            print(f"... {i}/{len(candidates)}", file=sys.stderr)
            portal._p_jar.cacheGC()
        try:
            obj = get_object()
        except (AttributeError, KeyError):
            print(f"WARNING unable to get {path}", file=sys.stderr)
            continue
        changes = analyze(obj)
        errors.extend((path, c) for c in changes if "error" in c)
        changes = [c for c in changes if "error" not in c]
        if changes:
            pages.append((path, changes))

    pages.sort(key=lambda p: -sum(c["old_bytes"] - c["new_bytes"] for c in p[1]))
    for path, changes in pages:
        print(path)
        for c in changes:
            print(f"    {format_change(c)}")

    old = sum(c["old_bytes"] for _, cs in pages for c in cs)
    new = sum(c["new_bytes"] for _, cs in pages for c in cs)
    print()
    print(f"Analyzed: {len(seen)}  Would modify: {len(pages)} pages")
    if old:
        print(f"Size: {human_size(old)} -> {human_size(new)} (-{100 - new * 100 / old:.0f}%)")
    for path, c in errors:
        print(f'ERROR (not optimizable) {path} "{c["filename"]}": {c["error"]}')

    transaction.abort()


main()
