=================
Datenguide Python
=================


.. image:: https://img.shields.io/pypi/v/datenguide_python.svg
        :target: https://pypi.python.org/pypi/datenguide_python

.. image:: https://img.shields.io/travis/AlexandraKapp/datenguide_python.svg
        :target: https://travis-ci.org/AlexandraKapp/datenguide_python

.. image:: https://readthedocs.org/projects/datenguide-python/badge/?version=latest
        :target: https://datenguide-python.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Python Wrapper for the Datenguide API.


* Free software: MIT license
* Documentation: https://datenguide-python.readthedocs.io.


Features
--------

* TODO

## Create a Query

A query is created with the QueryBuilder. 
According to the Datenguide API it either needs a region or a parent region specified. 
Also, at least one desired field must be defined. 
Optionally, a filter can be applied with args. 
Optionally, the administration level the statstics shall be returned from can be specified with nuts and lau. 
See for full documentation of the API: https://github.com/datenguide/datenguide-api

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
