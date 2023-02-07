# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import quickInstallProduct
from plone.testing import z2
from redturtle.volto.testing import RedturtleVoltoLayer
from redturtle.volto.testing import RedturtleVoltoRestApiLayer
from zope.configuration import xmlconfig
from zope.globalrequest import setRequest

import collective.dexteritytextindexer
import collective.MockMailHost
import collective.taxonomy
import collective.venue
import collective.volto.cookieconsent
import collective.volto.dropdownmenu
import collective.volto.formsupport
import collective.volto.secondarymenu
import collective.volto.socialsettings
import collective.volto.subfooter
import collective.volto.subsites
import design.plone.contenttypes
import design.plone.policy
import eea.api.taxonomy
import plone.app.caching
import plone.app.contentlisting
import plone.formwidget.geolocation
import plone.restapi
import redturtle.bandi
import redturtle.faq
import redturtle.volto
import redturtle.voltoplugin.editablefooter
import rer.customersatisfaction
import souper.plone


class FauxRequest(dict):
    URL = "http://nohost"


# TODO: dunno how to fix this
# File "/Users/martina/progetti/docker-compose-dev/src/design.plone.policy/src/
# design/plone/policy/setuphandlers.py", line 58, in post_install
#     create_menu()
#   File "/Users/martina/progetti/docker-compose-dev/src/design.plone.policy/src/
# design/plone/policy/utils.py", line 318, in create_menu
#     json_serialized = getMultiAdapter((x, request), ISerializeToJsonSummary)()
#   File "/opt/buildoutcache/egg-cache/plone.restapi-8.32.4-py3.8.egg/plone/
# restapi/serializer/summary.py", line 91, in __call__
#     obj = IContentListingObject(self.context)
# TypeError: ('Could not adapt', None,
# <InterfaceClass plone.app.contentlisting.interfaces.IContentListingObject>)
class DesignPlonePolicyLayer(RedturtleVoltoLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.

        self.loadZCML(package=collective.volto.formsupport)
        self.loadZCML(package=collective.venue)
        self.loadZCML(package=collective.volto.dropdownmenu)
        self.loadZCML(package=collective.volto.secondarymenu)
        self.loadZCML(package=collective.volto.socialsettings)
        self.loadZCML(package=collective.volto.subsites)
        self.loadZCML(package=redturtle.volto)
        self.loadZCML(package=collective.taxonomy)
        self.loadZCML(package=eea.api.taxonomy)
        self.loadZCML(name="overrides.zcml", package=design.plone.contenttypes)
        xmlconfig.file(
            "configure.zcml",
            design.plone.contenttypes,
            context=configurationContext,
        )
        self.loadZCML(package=design.plone.policy)
        self.loadZCML(package=plone.app.caching)
        self.loadZCML(package=plone.formwidget.geolocation)
        self.loadZCML(package=redturtle.bandi)
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=plone.app.contentlisting)
        self.loadZCML(package=redturtle.voltoplugin.editablefooter)
        self.loadZCML(package=collective.volto.subfooter)
        self.loadZCML(package=rer.customersatisfaction)
        self.loadZCML(package=souper.plone)
        self.loadZCML(package=redturtle.faq)

    def setUpPloneSite(self, portal):
        super().setUpPloneSite(portal)
        request = portal.REQUEST
        setRequest(request)
        applyProfile(portal, "plone.app.caching:default")
        applyProfile(portal, "collective.taxonomy:default")
        applyProfile(portal, "eea.api.taxonomy:default")
        applyProfile(portal, "design.plone.policy:default")


DESIGN_PLONE_POLICY_FIXTURE = DesignPlonePolicyLayer()


DESIGN_PLONE_POLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(DESIGN_PLONE_POLICY_FIXTURE,),
    name="DesignPlonePolicyLayer:IntegrationTesting",
)


DESIGN_PLONE_POLICY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(DESIGN_PLONE_POLICY_FIXTURE,),
    name="DesignPlonePolicyLayer:FunctionalTesting",
)


DESIGN_PLONE_POLICY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        DESIGN_PLONE_POLICY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="DesignPlonePolicyLayer:AcceptanceTesting",
)


class DesignPlonePolicyRestApiLayer(RedturtleVoltoRestApiLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(DesignPlonePolicyRestApiLayer, self).setUpZope(app, configurationContext)

        self.loadZCML(package=collective.MockMailHost)
        self.loadZCML(package=collective.venue)
        self.loadZCML(package=collective.volto.dropdownmenu)
        self.loadZCML(package=redturtle.volto)
        self.loadZCML(package=collective.volto.formsupport)
        self.loadZCML(package=collective.volto.secondarymenu)
        self.loadZCML(package=collective.volto.socialsettings)
        self.loadZCML(package=collective.volto.subfooter)
        self.loadZCML(package=collective.volto.subsites)
        self.loadZCML(package=collective.taxonomy)
        self.loadZCML(package=eea.api.taxonomy)
        self.loadZCML(name="overrides.zcml", package=design.plone.contenttypes)
        xmlconfig.file(
            "configure.zcml",
            design.plone.contenttypes,
            context=configurationContext,
        )
        self.loadZCML(package=design.plone.policy)
        self.loadZCML(package=plone.app.caching)
        self.loadZCML(package=plone.formwidget.geolocation)
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=plone.app.contentlisting)
        self.loadZCML(package=redturtle.bandi)
        self.loadZCML(package=redturtle.faq)
        self.loadZCML(package=redturtle.voltoplugin.editablefooter)
        self.loadZCML(package=rer.customersatisfaction)
        self.loadZCML(package=souper.plone)

    def setUpPloneSite(self, portal):
        super().setUpPloneSite(portal)
        request = portal.REQUEST
        setRequest(request)
        applyProfile(portal, "plone.app.caching:default")
        applyProfile(portal, "collective.taxonomy:default")
        applyProfile(portal, "eea.api.taxonomy:default")
        applyProfile(portal, "design.plone.policy:default")
        quickInstallProduct(portal, "collective.MockMailHost")
        applyProfile(portal, "collective.MockMailHost:default")


DESIGN_PLONE_POLICY_API_FIXTURE = DesignPlonePolicyRestApiLayer()
DESIGN_PLONE_POLICY_API_INTEGRATION_TESTING = IntegrationTesting(
    bases=(DESIGN_PLONE_POLICY_API_FIXTURE,),
    name="DesignPlonePolicyRestApiLayer:Integration",
)

DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(DESIGN_PLONE_POLICY_API_FIXTURE, z2.ZSERVER_FIXTURE),
    name="DesignPlonePolicyRestApiLayer:Functional",
)
