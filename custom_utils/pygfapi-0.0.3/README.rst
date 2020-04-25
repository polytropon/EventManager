pygfapi
=======

Library for interacting with the `Gravity Forms Web API
<https://www.gravityhelp.com/documentation/article/web-api/>`_.

Not created, sponsored, or supported by Rocketgenius, Inc.

Prerequisites
-------------
#. `WordPress <https://wordpress.org/>`_ installed.
#. `Pretty  Permalinks <https://codex.wordpress.org/Using_Permalinks>`_
   enabled (anything other than ``http://example.com/?p=123``).
#. `Gravity Forms <http://www.gravityforms.com/>`_ plugin installed and
   activated.
#. `Web API <https://www.gravityhelp.com/documentation/article/web-api/>`_
   enabled (Forms > Settings > Web API).

Installation
------------

.. code-block:: bash

    $ python setup.py install

Usage
-----

.. code-block:: python

    >>> from pygfapi import Client
    >>> gf = Client("https://example.com/gravityformsapi/", "1234", "abcd")
    >>> form = gf.get_form(1)
    >>> print form[u"id"]
    1
    >>> print form[u"title"]
    u'Test Form'
    >>> form_1_entries = gf.get_form_entries(1)
    >>> print len(form_1_entries)
    3
    >>> for entry in form_1_entries:
    ...   print entry[u"id"]
    ...
    3
    2
    1
    >>> entries = gf.get_unread_entries(15)
    >>> for e in entries:
    ...   print e[u"id"]
    ...   e[u"is_read"] = 1
    ...
    60
    59
    58
    >>> response = gf.put_entries(entries)
    >>> print response
    Entries updated successfully

Running Tests
-------------

.. code-block:: bash

    $ python -m unittest discover

License
-------
GNU General Public License, Version 3 (see LICENSE).

Copyright
---------
2016 `Arlington County Government <https://www.arlingtonva.us>`_.