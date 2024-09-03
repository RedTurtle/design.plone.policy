# -*- coding: utf-8 -*-
import collective.feedback
import collective.MockMailHost
import collective.taxonomy
import collective.volto.cookieconsent
import collective.volto.dropdownmenu
import collective.volto.formsupport
import collective.volto.secondarymenu
import collective.volto.slimheader
import collective.volto.socialsettings
import collective.volto.subfooter
import collective.volto.subsites
import collective.z3cform.datagridfield
import design.plone.contenttypes
import design.plone.policy
import eea.api.taxonomy
import plone.app.contentlisting
import redturtle.faq
import redturtle.voltoplugin.editablefooter
import souper.plone
from design.plone.contenttypes.testing import (
    DesignPloneContenttypesLayer,
    DesignPloneContenttypesRestApiLayer,
)
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting, IntegrationTesting, applyProfile
from plone.testing import z2
from zope.globalrequest import setRequest


class FauxRequest(dict):
    URL = "http://nohost"


class DesignPlonePolicyLayer(DesignPloneContenttypesLayer):
    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.

        super().setUpZope(app, configurationContext)
        self.loadZCML(package=design.plone.policy)
        self.loadZCML(package=collective.feedback)
        self.loadZCML(package=collective.volto.formsupport)
        self.loadZCML(package=collective.volto.cookieconsent)
        self.loadZCML(package=collective.volto.dropdownmenu)
        self.loadZCML(package=collective.volto.secondarymenu)
        self.loadZCML(package=collective.volto.socialsettings)
        self.loadZCML(package=collective.volto.subsites)
        self.loadZCML(package=redturtle.voltoplugin.editablefooter)
        self.loadZCML(package=collective.volto.subfooter)
        self.loadZCML(package=collective.volto.slimheader)
        self.loadZCML(package=collective.taxonomy)
        self.loadZCML(package=eea.api.taxonomy)
        self.loadZCML(name="overrides.zcml", package=design.plone.contenttypes)
        self.loadZCML(package=plone.app.contentlisting)
        self.loadZCML(package=souper.plone)
        self.loadZCML(package=redturtle.faq)

    def setUpPloneSite(self, portal):
        super().setUpPloneSite(portal)
        request = portal.REQUEST
        setRequest(request)
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


class DesignPlonePolicyLimitRootAddablesLayer(DesignPlonePolicyLayer):
    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.

        super().setUpZope(app, configurationContext)
        self.loadZCML(package=design.plone.policy)

    def setUpPloneSite(self, portal):
        super().setUpPloneSite(portal)
        request = portal.REQUEST
        setRequest(request)
        import pdb

        pdb.set_trace()
        applyProfile(portal, "design.plone.policy.limit_root_addables:default")


DESIGN_PLONE_POLICY_LIMIT_ROOT_ADDABLES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(DESIGN_PLONE_POLICY_INTEGRATION_TESTING,),
    name="DesignPlonePolicyLimitRootAddablesLayer:IntegrationTesting",
)


class DesignPlonePolicyRestApiLayer(DesignPloneContenttypesRestApiLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super().setUpZope(app, configurationContext)

        self.loadZCML(package=collective.z3cform.datagridfield)
        self.loadZCML(package=design.plone.policy)
        self.loadZCML(package=collective.feedback)
        self.loadZCML(package=collective.volto.formsupport)
        self.loadZCML(package=collective.volto.cookieconsent)
        self.loadZCML(package=collective.volto.dropdownmenu)
        self.loadZCML(package=collective.volto.secondarymenu)
        self.loadZCML(package=collective.volto.socialsettings)
        self.loadZCML(package=collective.volto.subsites)
        self.loadZCML(package=redturtle.voltoplugin.editablefooter)
        self.loadZCML(package=collective.volto.subfooter)
        self.loadZCML(package=collective.volto.slimheader)
        self.loadZCML(package=redturtle.volto)
        self.loadZCML(package=collective.taxonomy)
        self.loadZCML(package=eea.api.taxonomy)
        self.loadZCML(name="overrides.zcml", package=design.plone.contenttypes)
        self.loadZCML(package=design.plone.policy)
        self.loadZCML(package=plone.app.contentlisting)
        self.loadZCML(package=redturtle.faq)
        self.loadZCML(package=souper.plone)
        self.loadZCML(package=redturtle.faq)

    def setUpPloneSite(self, portal):
        super().setUpPloneSite(portal)
        request = portal.REQUEST
        setRequest(request)
        applyProfile(portal, "design.plone.policy:default")


DESIGN_PLONE_POLICY_API_FIXTURE = DesignPlonePolicyRestApiLayer()
DESIGN_PLONE_POLICY_API_INTEGRATION_TESTING = IntegrationTesting(
    bases=(DESIGN_PLONE_POLICY_API_FIXTURE,),
    name="DesignPlonePolicyRestApiLayer:Integration",
)

DESIGN_PLONE_POLICY_API_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(DESIGN_PLONE_POLICY_API_FIXTURE, z2.ZSERVER_FIXTURE),
    name="DesignPlonePolicyRestApiLayer:Functional",
)
