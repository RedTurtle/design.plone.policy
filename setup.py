# -*- coding: utf-8 -*-
"""Installer for the design.plone.policy package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="design.plone.policy",
    version="5.0.17.dev0",
    description="Pacchetto per creare un sito Agid su Plone",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone",
    author="RedTurtle Technology",
    author_email="sviluppo@redturtle.it",
    url="https://github.com/collective/design.plone.policy",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/design.plone.policy",
        "Source": "https://github.com/RedTurtle/design.plone.policy",
        "Tracker": "https://github.com/RedTurtle/design.plone.policy/issues",
        # 'Documentation': 'https://design.plone.policy.readthedocs.io/en/latest/',
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["design", "design.plone"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "setuptools",
        "redturtle.volto",
        "design.plone.contenttypes>=6.0.0.dev0",
        "collective.feedback",
        "collective.volto.dropdownmenu",
        "collective.volto.formsupport[honeypot]>=3.2.0",
        "collective.volto.secondarymenu",
        "collective.volto.socialsettings",
        "collective.volto.slimheader",
        "collective.volto.subsites",
        "collective.volto.subfooter",
        "redturtle.voltoplugin.editablefooter",
        "redturtle.faq",
        "redturtle.rssservice",
        "iw.rejectanonymous",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            "plone.testing>=5.0.0",
            "plone.app.contenttypes",
            "plone.app.robotframework[debug]",
            "collective.MockMailHost",
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
