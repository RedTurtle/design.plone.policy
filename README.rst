===================
Design Plone Policy
===================

Pacchetto di policy per un sito Plone AGID.

Features
========

Installando questo pacchetto, si inizializza un sito Plone Agid.

Creazione struttura del sito
============================

All'installazione di questo prodotto, oltre che l'installazione di tutte le dipendenze,
viene anche eseguita la creazione in automatico di una serie di cartelle utili per la 
gestione dei contenuti richiesta da Agid.


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
        'topics': [
            {
                '@id': '',
                'path': '',
                'title': '',
            },
            ...
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

Se l'invio va a buon fine, viene tornata una risposta con `204`.

Installazione
=============

Per installare design.plone.policy bisogna per prima cosa aggiungerlo al buildout::

    [buildout]

    ...

    eggs =
        design.plone.policy


e poi lanciare il buildout con ``bin/buildout``.

Successivamente va installato dal pannello di controllo di Plone.

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
