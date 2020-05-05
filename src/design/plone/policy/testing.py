# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.restapi.testing import PloneRestApiDXLayer

from plone.testing import z2

import collective.folderishtypes
import collective.venue
import design.plone.contenttypes
import design.plone.policy
import plone.formwidget.geolocation
import plone.restapi


class DesignPlonePolicyLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.

        self.loadZCML(package=collective.folderishtypes)
        self.loadZCML(package=collective.venue)
        self.loadZCML(package=design.plone.contenttypes)
        self.loadZCML(package=design.plone.policy)
        self.loadZCML(package=plone.formwidget.geolocation)
        self.loadZCML(package=plone.restapi)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'design.plone.policy:default')


DESIGN_PLONE_POLICY_FIXTURE = DesignPlonePolicyLayer()


DESIGN_PLONE_POLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(DESIGN_PLONE_POLICY_FIXTURE,),
    name='DesignPlonePolicyLayer:IntegrationTesting',
)


DESIGN_PLONE_POLICY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(DESIGN_PLONE_POLICY_FIXTURE,),
    name='DesignPlonePolicyLayer:FunctionalTesting',
)


DESIGN_PLONE_POLICY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        DESIGN_PLONE_POLICY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='DesignPlonePolicyLayer:AcceptanceTesting',
)


class DesignPlonePolicyRestApiLayer(PloneRestApiDXLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(DesignPlonePolicyRestApiLayer, self).setUpZope(
            app, configurationContext
        )

        self.loadZCML(package=collective.folderishtypes)
        self.loadZCML(package=collective.venue)
        self.loadZCML(package=design.plone.contenttypes)
        self.loadZCML(package=design.plone.policy)
        self.loadZCML(package=plone.formwidget.geolocation)
        self.loadZCML(package=plone.restapi)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'design.plone.policy:default')


DESIGN_PLONE_POLICY_API_FIXTURE = DesignPlonePolicyRestApiLayer()
DESIGN_PLONE_POLICY_API_INTEGRATION_TESTING = IntegrationTesting(
    bases=(DESIGN_PLONE_POLICY_API_FIXTURE,),
    name="DesignPlonePolicyRestApiLayer:Integration",
)

DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(DESIGN_PLONE_POLICY_API_FIXTURE, z2.ZSERVER_FIXTURE),
    name="DesignPlonePolicyRestApiLayer:Functional",
)
