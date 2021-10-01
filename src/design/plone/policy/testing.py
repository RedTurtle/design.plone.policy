# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import quickInstallProduct
from plone.restapi.testing import PloneRestApiDXLayer
from plone.testing import z2
from zope.globalrequest import setRequest

import collective.dexteritytextindexer
import collective.folderishtypes
import collective.MockMailHost
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
import kitconcept.seo
import plone.app.caching
import plone.formwidget.geolocation
import plone.restapi
import redturtle.bandi
import redturtle.volto
import redturtle.voltoplugin.editablefooter


class FauxRequest(dict):
    URL = "http://nohost"


class DesignPlonePolicyLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.

        self.loadZCML(package=collective.volto.formsupport)
        self.loadZCML(package=collective.folderishtypes)
        self.loadZCML(package=collective.venue)
        self.loadZCML(package=collective.volto.cookieconsent)
        self.loadZCML(package=collective.volto.dropdownmenu)
        self.loadZCML(package=collective.volto.secondarymenu)
        self.loadZCML(package=collective.volto.socialsettings)
        self.loadZCML(package=collective.volto.subsites)
        self.loadZCML(package=design.plone.contenttypes)
        self.loadZCML(package=design.plone.policy)
        self.loadZCML(package=kitconcept.seo)
        self.loadZCML(package=plone.app.caching)
        self.loadZCML(package=plone.formwidget.geolocation)
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=redturtle.bandi)
        self.loadZCML(package=redturtle.volto)
        self.loadZCML(package=redturtle.voltoplugin.editablefooter)
        self.loadZCML(package=collective.dexteritytextindexer)
        self.loadZCML(package=collective.volto.subfooter)

    def setUpPloneSite(self, portal):
        request = FauxRequest()
        setRequest(request)
        applyProfile(portal, "plone.app.caching:default")
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


class DesignPlonePolicyRestApiLayer(PloneRestApiDXLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(DesignPlonePolicyRestApiLayer, self).setUpZope(app, configurationContext)

        self.loadZCML(package=collective.folderishtypes)
        self.loadZCML(package=collective.MockMailHost)
        self.loadZCML(package=collective.venue)
        self.loadZCML(package=collective.volto.cookieconsent)
        self.loadZCML(package=collective.volto.dropdownmenu)
        self.loadZCML(package=collective.volto.formsupport)
        self.loadZCML(package=collective.volto.secondarymenu)
        self.loadZCML(package=collective.volto.socialsettings)
        self.loadZCML(package=collective.volto.subsites)
        self.loadZCML(package=design.plone.contenttypes)
        self.loadZCML(package=design.plone.policy)
        self.loadZCML(package=kitconcept.seo)
        self.loadZCML(package=plone.app.caching)
        self.loadZCML(package=plone.formwidget.geolocation)
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=redturtle.bandi)
        self.loadZCML(package=redturtle.volto)
        self.loadZCML(package=redturtle.voltoplugin.editablefooter)
        self.loadZCML(package=collective.volto.subfooter)

    def setUpPloneSite(self, portal):
        request = FauxRequest()
        setRequest(request)
        applyProfile(portal, "plone.app.caching:default")
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
