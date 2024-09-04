from design.plone.policy.patches.collective_volto_formsupport import (
    patch_FormDataExportGet_get_data,
)
from design.plone.policy.patches.collective_volto_formsupport import (
    patch_FormDataStore_methods,
)
from design.plone.policy.patches.collective_volto_formsupport import (
    patch_SubmitPost_reply,
)


def apply():
    patch_FormDataExportGet_get_data()
    patch_SubmitPost_reply()
    patch_FormDataStore_methods()
