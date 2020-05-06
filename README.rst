===================
Design Plone Policy
===================

Pacchetto di policy per un sito Plone AGID.

Features
========

Installando questo pacchetto, si inizializza un sito Plone Agid.

Endpoint per plone.restapi
==========================

@search-filters
---------------

Questo endpoint serve al frontend di Volto, per popolare il menu e i filtri per la ricerca::

    > curl -i http://localhost:8080/Plone/@search-filters -H 'Accept: application/json'

Ritorna un json con le sezioni principali e la lista degli argomenti::

    {
        'sections':{
            'amministrazione':{
                '@id': '',
                'path': '',
                'title': '',
                'items': [
                    {
                        '@id': '',
                        'path': '',
                        'title': '',
                    },
                    ...
                ]
            }
            'documenti-e-dati': {...}
            'novita': {...}
            'servizi': {...}
        },
        'arguments': [
            {
                '@id': '',
                'path': '',
                'title': '',
            },
            ...
        ]
    }

Installazione
=============

Per installare design.plone.policy bisogna per prima cosa aggiungerlo al buildout::

    [buildout]

    ...

    eggs =
        design.plone.policy


e poi lanciare il buildout con ``bin/buildout``.

Successivamente va installato dal pannello di controllo di Plone.


Contribuisci
============

- Issue Tracker: https://github.com/redturtle/design.plone.policy/issues
- Codice sorgente: https://github.com/redturtle/design.plone.policy


Licenza
=======

Questo progetto è rilasciato con licenza GPLv2.

Autori
======

Questo progetto è stato sviluppato da **RedTurtle Technology**.

.. image:: https://avatars1.githubusercontent.com/u/1087171?s=100&v=4
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
