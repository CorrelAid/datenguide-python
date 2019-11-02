Datenguide Python
=================


.. image:: https://img.shields.io/pypi/v/datenguidepy.svg
        :target: https://pypi.python.org/pypi/datenguidepy

.. image:: https://img.shields.io/travis/CorrelAid/datenguide-python.svg
        :target: https://travis-ci.org/CorrelAid/datenguide-python

.. image:: https://readthedocs.org/projects/datenguidepy/badge/?version=latest
        :target: https://datenguidepy.readthedocs.io/en/latest/readme/#quick-start



The package provides easy access to German publicly available `regional statistics`_.
It does so by providing a wrapper for the `GraphQL API of the Datenguide project`_.


* Free software: MIT license
* Documentation:  https://datenguidepy.readthedocs.io/


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
-----------

============
Install
============
To use the package install the package (command line): 

.. code-block:: python

   pip install datenguidepy

============
Setup query
============
Within your python file or notebook:

**1. Import the package**

.. code-block:: python

    from datenguidepy import Query

**2. Creating a query**

- either for single regions

.. code-block:: python

    query = Query.region('01')

- or for all subregions a region (e.g. all Kommunen in a Bundesland)

.. code-block:: python

   query_allregions = Query.allRegions(parent='01')

- How to get IDs for regions? see below "Get information on fields and meta data"

**3. Add statistics (fields)**

- Add statistics you want to get data on

.. code-block:: python

    field = query.add_field('BEV001')

- How do I find the short name of the statistics? see below "Get information on fields and meta data"

**4. Add filters**
    A field can also be added with filters. E.g. you can specify, that only data from a specific year     shall    be returned.

.. code-block:: python

    field.add_args({'year': [2014, 2015]})

**5. Add subfield**
    A set of default subfields are defined for all statistics (year, value, source). 
    If additional fields (columns in the results table) shall be returned, they can be specified as a field argument.

.. code-block:: python

    field.add_field('GES') # Geschlecht

    # by default the summed value for a field is returned. 
    # E.g. if the field "Geschlecht" is added, the results table will show "None" in each row, 
    # which means total value for women and man.
    # To get disaggregated values, they speficically need to be passed as args. 
    # If e.g. only values for women shall be returned, use:

    field.add_args({'GES': 'GESW'})

    # if all possible enum values shall be returned disaggregated, pass 'ALL':

    field.add_args({'GES': 'ALL'})

**6. Get results**
    Get the results as a Pandas DataFrame

.. code-block:: python

    df = query.results()


=======================================
Get information on fields and meta data
=======================================

**Get information on region ids**

.. code-block:: python

    from datenguidepy import get_all_regions

    get_all_regions()

Use pandas *query()* functionality to get specific regions. E.g., if you want to get all IDs on "Bundeländer" use.
For more information on "nuts" levels see Wikipedia_.

.. code-block:: python

    get_all_regions().query("level == 'nuts1'")



**Get information on statistic shortnames**

.. code-block:: python

    from datenguidepy import get_statistics

    get_statistics()

**Get information on single fields**

You can further information about description, possible arguments, fields and enum values on a field you added to a query.

.. code-block:: python

    query = Query.region("01")
    field = query.add_field("BEV001")
    field.get_info()

===================
Further information
===================

For detailed examples see the notebooks within the use_case_ folder.

For a detailed documentation of all statistics and fields see the Datenguide API.



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
.. _use_case: https://github.com/CorrelAid/datenguide-python/tree/master/use_case
.. _`credited according to the "Datenlizenz Deutschland – Namensnennung – Version 2.0"`: https://www.regionalstatistik.de/genesis/online;sid=C636A83329D19AF20E3A4F9E767576A9.reg2?Menu=Impressum
.. _Wikipedia: https://de.wikipedia.org/wiki/NUTS:DE#Liste_der_NUTS-Regionen_in_Deutschland_(NUTS_2016)
