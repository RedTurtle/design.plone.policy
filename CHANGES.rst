Changelog
=========


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
