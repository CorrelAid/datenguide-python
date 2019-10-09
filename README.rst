Datenguide Python
=================


.. image:: https://img.shields.io/pypi/v/datenguidepy.svg
        :target: https://pypi.python.org/pypi/datenguidepy

.. image:: https://img.shields.io/travis/CorrelAid/datenguide-python.svg
        :target: https://travis-ci.org/CorrelAid/datenguide-python

.. image:: https://readthedocs.org/projects/datenguide-python/badge/?version=latest
        :target: https://datenguide-python.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status



The package provides easy access to German publicly available `regional statistics`_.
It does so by providing a wrapper for the `GraphQL API of the Datenguide project`_.


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

Quick Start
--------

============
Install
============
  To use the package install the package (command line): 

``pip install datenguidepy``

============
Setup query
============
    Within your python file or notebook:

1. **Import the package**

``from datenguidepy.query_builder import Query``

2. **Creating a query**

- either for single regions
``query = Query.region('01')``

- or for all subregions a region (e.g. all Kommunen in a Bundeland)``

``query_allregions = Query.allRegions(parent='01')``

3. **Add statistics (fields)**
    Add statistics you want to get data on
    (How do I find the short name of the statistics?(LINK))

``query.add_field('BEV001')``

4. **Add filters**
    A field can also be added with filters. E.g. you can specify, that only data from a specific year     shall    be returned.

``query.add_field('BEV001', args={year:'2017'})``

5. **Add subfield**
    A set of default subfields are defined for all statistics (year, value, source). 
    If additional fields shall be returned, they can be specified as a field argument.

``query.add_field('BEV001', field=['GES'])``

6. **Get results**
    Get the results as a Pandas DataFrame

``df = query.results()``


============
Get information on fields and meta data
============

*TODO*

============
Further information
============

  For detailed examples see the notebooks in the use_case folder.

  For a detailed documentation of all statistics and fields see the _Datenguide API.



Credits
-------
All this builds on the great work of Datenguide_ and their GraphQL API `datenguide/datenguide-api`_ 

The data is retrieved via the Datenguide API from the "Statistische Ämter des Bundes und der Länder". 
Data being used via this package has to be `credited according to the "Datenlizenz Deutschland – Namensnennung – Version 2.0"`_.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`datenguide/datenguide-api`: https://github.com/datenguide/datenguide-api
.. _Datenguide: https://datengui.de/
.. _`GraphQL API of the Datenguide project`: https://github.com/datenguide/datenguide-api
.. _`regional statistics`: https://www.regionalstatistik.de/genesis/online/logon
.. _`credited according to the "Datenlizenz Deutschland – Namensnennung – Version 2.0"`: https://www.regionalstatistik.de/genesis/online;sid=C636A83329D19AF20E3A4F9E767576A9.reg2?Menu=Impressum
