# -*- coding: utf-8 -*-
from design.plone.policy.block_images import human_size
from design.plone.policy.block_images import optimize_image_with_stats
from design.plone.policy.interfaces import IDesignPlonePolicyLayer
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

import logging

logger = logging.getLogger(__name__)


class BlockImageOptimizerBase:
    """Resize and convert to WebP the base64 image stored inline in the block.

    Registered for any context (contents, site root, blocks fields): in Plone 6
    the site root provides both IBlocks and IPloneSiteRoot, and a pair of
    adapters would run twice on it.
    """

    # run before redturtle.volto GenericResolveUIDDeserializer (order 200), that
    # otherwise calls path2uid on the whole base64 string
    order = 10
    block_type = None
    disabled = False

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        new_value, stats = optimize_image_with_stats(block.get("image"))
        if new_value:
            block["image"] = new_value
            logger.info(
                "[%s] optimized %s image %r: %s -> %s",
                "/".join(self.context.getPhysicalPath()),
                self.block_type,
                stats["filename"],
                human_size(stats["old_bytes"]),
                human_size(stats["new_bytes"]),
            )
        return block


@implementer(IBlockFieldDeserializationTransformer)
@adapter(Interface, IDesignPlonePolicyLayer)
class TextCardWithImageDeserializer(BlockImageOptimizerBase):
    block_type = "testo_riquadro_immagine"


@implementer(IBlockFieldDeserializationTransformer)
@adapter(Interface, IDesignPlonePolicyLayer)
class AlertDeserializer(BlockImageOptimizerBase):
    block_type = "alert"
