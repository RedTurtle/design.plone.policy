# -*- coding: utf-8 -*-
from design.plone.policy.upgrades import logger


def to_3105(context):
    """Superseded by 3106, that optimizes the block images while moving them
    to Image contents."""
    logger.info(
        "[3104 - 3105] Nothing to do: the block images are optimized by the "
        "3105 - 3106 upgrade step."
    )
