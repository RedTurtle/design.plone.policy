===================
Design Plone Policy
===================

Pacchetto di policy per un sito Plone AGID.

.. image:: https://img.shields.io/pypi/v/design.plone.policy.svg
    :target: https://pypi.org/project/design.plone.policy/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/design.plone.policy.svg?style=plastic
    :target: https://pypi.org/project/design.plone.policy/
    :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/dm/design.plone.policy.svg
    :target: https://pypi.org/project/design.plone.policy/
    :alt: Number of PyPI downloads

.. image:: https://img.shields.io/pypi/l/design.plone.policy.svg
    :target: https://pypi.org/project/design.plone.policy/
    :alt: License

.. image:: https://github.com/RedTurtle/design.plone.policy/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/RedTurtle/design.plone.policy/actions
    :alt: Tests

.. image:: https://coveralls.io/repos/github/RedTurtle/design.plone.policy/badge.svg?branch=main
    :target: https://coveralls.io/github/RedTurtle/design.plone.policy?branch=main
    :alt: Coverage

Features
========

Installando questo pacchetto, si inizializza un sito Plone Agid.

Creazione struttura del sito
============================

All'installazione di questo prodotto, oltre che l'installazione di tutte le dipendenze,
viene anche eseguita la creazione in automatico di una serie di cartelle utili per la
gestione dei contenuti richiesta da Agid.

Compatibilità
=============

* Plone 6.0, design.plone.policy 5.*, design.plone.contenttypes 6.*
* Plone 5.2, design.plone.policy 4.*, design.plone.contenttypes 5.*

Tipi ricercabili
================

Installando questo prodotto, si disabilitano alcuni tipi ricercabili (così non vengon mostrati in @search-filters).


Customer satisfaction
=====================

Viene installato un plugin aggiuntivo (rer.customersatisfaction) per poter esprimere voti sulle pagine del portale Agid.

Per poter usare questo prodotto, va salvata la chiave privata per recaptcha v3 in una variabile d'ambiente (RECAPTCHA_PRIVATE_KEY).
La chiave pubblica viene usata dal client Volto.


Endpoint per plone.restapi
==========================

@search-filters
---------------

Questo endpoint serve al frontend di Volto, per popolare il menu e i filtri per la ricerca::

    > curl -i http://localhost:8080/Plone/@search-filters -H 'Accept: application/json'

Ritorna un json con le sezioni principali, la lista degli argomenti e i tipi di contenuto ricercabili (tradotti)::

    {
        "sections":{
            "amministrazione":{
                "@id": "",
                "path": "",
                "title": "",
                "items": [
                    {
                        "@id": "",
                        "path": "",
                        "title": "",
                    },
                    ...
                ]
            }
            "documenti-e-dati": {...}
            "novita": {...}
            "servizi": {...}
        },
        "topics": [
            {
                "@id": "",
                "path": "",
                "title": "",
            },
            ...
        ],
        "portal_types": [
            ...
            {
              "label": "Document",
              "id": "Page"
            }
            ...
        ]
    }

@search-bandi-filters
---------------------

Questo endpoint serve al frontend di Volto, per popolare il menu e i filtri per la ricerca dei bandi::

    > curl -i http://localhost:8080/Plone/@search-bandi-filters -H 'Accept: application/json'

Ritorna un json con la lista degli uffici (UO) referenziati da almeno un Bando e la lista delle parole chiave utilizzate dai Bandi::

    {
      "offices": [
        {
          "key": "87bb96d90b6e42ee9db01ab2ab7543d5",
          "label": "uo 1"
        }
      ],
      "subjects": [
        "bar",
        "foo"
      ]
    }

@send-action-form
-----------------

Questo endpoint va chiamato su un contesto con i blocchi abilitati e
serve al frontend di Volto, per inviare via mail il form compilato::

    > curl -i -X POST http://localhost:8080/Plone/document/@send-action-form -H 'Accept: application/json' -H 'Content-Type: application/json' --data-raw '{"from": "john@doe.com", "message": "Just want to say hi.", "block_id": "123456"}'

All'endpoint vanno passati i seguenti parametri:

- **block_id** [*obbligatorio*]: l'id del blocco di tipo "*form*" che è stato compilato
- **message** [*obbligatorio*]: il messaggio da inviare
- **from**: l'indirizzo email del mittente. Se non presente, viene utilizzato il campo *default_from* del blocco
- **subject**: l'oggetto della mail. Se non presente, viene utilizzato il campo *default_subject* del blocco
- **attachments**: eventuali allegati riferiti a campi "file upload" inseriti nel form.

La struttura degli attachments è la seguente::

    {
        "block_id": "foo",
        ...
        "attachments": {
            "field_id": {
                "data": "the content of the file",
                "content-type": "application/pdf",
                "filename": "example.pdf"
            }
        }
    }

Se l'invio va a buon fine, viene tornata una risposta con `204`.

Amministrazione trasparente
===========================

La vista "crea_area_trasparenza" crea la struttura per l'area "Amministrazione Trasparente".
Si può lanciare dalla root del sito.


Vocabolari per gli anonimi
==========================

**redturtle.volto** permette di esporre dei vocabolari anche agli utenti anonimi.

In questo prodotto aggiungiamo quelli che servono per io-comune.


Access inactive portal content
==============================

**redturtle.volto** personalizza questo ruolo per permettere ad utenti redazioniali di accedere a contenuti
con data di pubblicazione nel futuro o scaduti (di base quel permesso ce l'hanno solo gli admin).


Installazione
=============

Per installare design.plone.policy bisogna per prima cosa aggiungerlo al buildout::

    [buildout]

    ...

    eggs =
        design.plone.policy


e poi lanciare il buildout con ``bin/buildout``.

Successivamente va installato dal pannello di controllo di Plone.

Forzare autenticazione
----------------------

Se le richieste arrivano con un header X-ForceAuth Plone forza l'autenticazione per quelle richieste,
il meccanismo è utile ad esempiop se si vuole fare accedere alla ZMI o alle interfacce Plone legacy
senza però esporle pubblicamente.


Test con Volto standalone
-------------------------

Si può usare questo prodotto anche da solo, per fare delle demo veloci di Volto, senza
dover per forza creare un nuovo progetto/buildout.

E' presente un file `buildout.cfg` anche in questo prodotto, quindi basta lanciare il buildout ed avviare l'istanza.

Il sito Plone sarà esposto sulla porta standard (**8080**) ed è già configurato per accettare chiamate dalla porta **3000**
(quindi Volto dovrà girare su quella porta, che poi è il suo default).


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
