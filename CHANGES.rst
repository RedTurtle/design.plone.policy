Changelog
=========

5.0.0 (2023-03-24)
------------------

- Fix test dependencies.
  [cekk]

5.0.0a5 (2023-03-01)
--------------------

- Update upgrade scripts to call design.plone.contenttypes
  upgrade steps to version 7008
  Install collective.feedback when install design.plone.policy
  [lucabel]


5.0.0a4 (2023-02-20)
--------------------

- Upgrade script to generate first and second level menu
  due to a couple of typo
  [lucabel]


5.0.0a3 (2023-02-16)
--------------------

- Upgrade footer initialization
  [lucabel]
- Add collective.feedback to setup.py
  [eikichi18]


5.0.0a2 (2023-01-13)
--------------------

- Upgrades for new AGID AI
  [lucabel]


5.0.0a1 (2023-01-12)
--------------------

- remove collective.dexteritytextindexer dependency.
  [cekk]
- adjustments to the pnrr.
  [deodorhunter, lucabek, eikichi18]


4.0.2 (2023-01-30)
------------------

- Aggiunto ordinamento per il filtro "Argomenti" nella pagina
  di ricerca.
  [lucabel]


4.0.1 (2022-12-07)
------------------

- Add "data-element" to custom attributes in html filters.
  [cekk]


4.0.0 (2022-11-07)
------------------

- Fix formsupport dependency to use honeypot and upgrade-step to set it in forms.
  [cekk]

3.0.0 (2022-08-16)
------------------

- Remove unused dependency in tests.
  [cekk]

2.12.0 (2022-07-05)
-------------------

- scrub sensitive information for sentry
  [mamico]
- Improve @bandi-search-filters speed.
  [cekk]

2.11.3 (2022-01-27)
-------------------

- Fix upgrade-step.
  [cekk]


2.11.2 (2022-01-27)
-------------------

- Fix image miniature with 65536.
  [cekk]

2.11.1 (2022-01-27)
-------------------

- Add new image miniature (midi).
  [cekk]

2.11.0 (2021-12-27)
-------------------

- Add default blocks to automatically created pages.
  [cekk]


2.10.0 (2021-12-01)
-------------------

- Remove enabled_vocabularies implementation because in recent plone.restapi (>8.15.2) there is a standard way.
  [cekk]


2.9.1 (2021-11-04)
------------------

- Install redturtle.faq by default.
  [cekk]


2.9.0 (2021-11-03)
------------------

- Add redturtle.faq dependency (it will not be installed by default).
  [cekk]

2.8.0 (2021-10-22)
------------------

- Add rer.customersatisfaction dependency.
  [cekk]


2.7.0 (2021-10-11)
------------------

- p.a.caching rules for rest api services.
  [cekk]


2.6.1 (2021-10-01)
------------------

- Updated blocks generation for "crea_area_trasparenza" view.
  [daniele]

2.6.0 (2021-09-29)
------------------

- Remove limited content-types in initial structure creation.
  [cekk]


2.5.0 (2021-09-20)
------------------

- Refactored search filters endpoints to be more efficient.
  [cekk]
- Can also add "Persona" in Politici folder.
  [cekk]
- Add collective.volto.subfooter as dependency.
  [cekk]

2.4.0 (2021-08-24)
------------------

- Add list of available vocabularies for Anonymous.
  [cekk]


2.3.0 (2021-07-07)
------------------

- Install collective.volto.subsites by default and add a set of colors.
  [cekk]


2.2.0 (2021-06-08)
------------------

- [new] @search-bandi-filters endpoint.
  [cekk]


2.1.2 (2021-05-14)
------------------

- [new] Content type 'Bando' is admitted by default in 'Documenti e dati' folder.
  [arsenico13]


2.1.1 (2021-05-04)
------------------

- Fix upgrade-step.
  [cekk]


2.1.0 (2021-05-04)
------------------

- Handle multiple twitter accounts in twitter endpoint.
  [cekk]
- Change twitter token field in registry (now is managed with interface).
  [cekk]


2.0.0 (2021-04-30)
------------------

- Update with new settings values from design.plone.contenttypes (version 3.0.0).
  [cekk]
- [dev] Fix CI
  [arsenico13]
- Add custom image scales
  [nzambello]
- **search-filters** endpoint now return also a list of searchable portal_types.
  [cekk]
- Disable some types from *types_not_searched*.
  [cekk]

1.1.0 (2021-03-24)
------------------

- Remove form route and add **collective.volto.formsupport** dependency.
  [cekk]


1.0.8 (2021-02-25)
------------------

- On install, set default search sections.
  [cekk]


1.0.7 (2021-02-19)
------------------

- Fix typo.
  [cekk]


1.0.6 (2021-02-19)
------------------

- Do not run dependencies when upgrading plone.app.registry.
  [cekk]

1.0.5 (2021-02-11)
------------------

- Install collective.volto.socialsettings by default.
  [cekk]


1.0.4 (2021-02-05)
------------------

- Add collective.volto.secondarymenu dependency.
  [cekk]
- Enable sitemap by default.
  [cekk]


1.0.3 (2021-01-28)
------------------

- Handle Unauthorized in search-filters endpoint.
  [cekk]


1.0.2 (2021-01-11)
------------------

- Manage also attachments in @send-action-form endpoint.
  [cekk]


1.0.1 (2020-12-18)
------------------

- Added view to create trasparenza structure.
  [daniele]

- Fixed folders creation when installing.
  [daniele]

- Add twitter-feed endpoint.
  [cekk]

1.0.0 (2020-12-07)
------------------

- Initial release.
  [cekk]
