Datenguide Python
=================


.. image:: https://img.shields.io/pypi/v/datenguidepy.svg
        :target: https://pypi.python.org/pypi/datenguidepy

.. image:: https://img.shields.io/travis/CorrelAid/datenguide-python.svg
        :target: https://travis-ci.org/CorrelAid/datenguide-python

.. image:: https://readthedocs.org/projects/datenguide-python/badge/?version=latest
        :target: https://datenguide-python.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status



The package provides easy access to German publicly available regional statistics.
It does so by providing a wrapper for the GraphQL API of the Datenguide project.


* Free software: MIT license
* Documentation: https://datenguide-python.readthedocs.io.


Features
--------

**Overview of available statistics and regions:**
  The package provides DataFrames with the available statistics and regions, which
  can be queried by the user without having to refer to expert knowledge on regional
  statistics or the documentation of the underlying GraphQL API

**Build and Execute Queries:**
  The package provides the user an object oriented interface to build queries that
  fetch certain statistics and return the results as a pandas DataFrame for
  further analysis.


Credits
-------
All this builds on the great work of Datenguide_ and their GraphQL API `datenguide/datenguide-api`_



This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`datenguide/datenguide-api`: https://github.com/datenguide/datenguide-api
.. _Datenguide: https://datengui.de/
