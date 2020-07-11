Datenguide Python
=================

The package provides easy access to German publicly available `regional statistics`_.
It does so by providing a wrapper for the `GraphQL API of the Datenguide project`_.


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
  
**Automatic inclusion of relevant meta data**
  Queries automatically retrieve some meta data along with the actual data
  to give the user more convenient access to the statistics without having to worry
  about too many technichal details
  
**Full fidelity data**
  The package provides full fidelity data access to the datenguide API.
  This allows all use cases to use precicely the data that they need
  if it is available. It also means that most data cleaning has to be done
  by the user.

Quick Start
-----------

============
Install
============
To use the package install the package (command line): 

.. code-block:: python

   pip install datenguidepy
   
============
Minimal example
============
To see the package work and obtain a DataFrame containing
some statistics, the followin constitutes a minimal example.

.. code-block:: python

    from datenguidepy import Query
    
    q = Query.region('01')
    q.add_field('BEV001')
    result_df = q.results()
    
    
================
Complex example
================

This example is intendend to illustrate many
of the package's features at the same time. The
idea is to give an impression of some of the possibilities.
A more detailed explanation of the functionality can be found
in the the rest of the documentation.

.. code-block:: python

    q = Query.region(['01','02'])
    stat = q.add_field('BEVSTD')
    stat.add_args({'year' : [2011,2012]})
    stat2 = q.add_field('AI1601')
    stat2.add_args({'year' : [2011,2012]})
    r = q.results(
        verbose_statistics = True,
        add_units = True,
    ).iloc[:,:7]
    
====  ====  ==================  ======  =============================================  =============  ============================  =============
  ..    id  name                  year    Verfügbares Einkommen je Einwohner (AI1601)  AI1601_unit      Bevölkerungsstand (BEVSTD)  BEVSTD_unit
====  ====  ==================  ======  =============================================  =============  ============================  =============
   0    01  Schleswig-Holstein    2011                                          20122  EUR                                 2802266  Anzahl
   1    01  Schleswig-Holstein    2012                                          20746  EUR                                 2806531  Anzahl
   0    02  Hamburg               2011                                          22695  EUR                                 1718187  Anzahl
   1    02  Hamburg               2012                                          22971  EUR                                 1734272  Anzahl
====  ====  ==================  ======  =============================================  =============  ============================  =============


=======================================
Get information on fields and meta data
=======================================

**Get information on region ids**

.. code-block:: python

   # from datenguidepy import get_regions

    get_regions()

Use pandas *query()* functionality to get specific regions. E.g., if you want to get all IDs on "Bundeländer" use.
For more information on "nuts" levels see Wikipedia_.

.. code-block:: python

    get_regions().query("level == 'nuts1'")



**Get information on statistic shortnames**

.. code-block:: python

  #  from datenguidepy import get_statistics

    get_statistics()
    # return statistical descriptions in English
    get_statistics(target_language = 'en')

**Get information on single fields**

You can further information about description, possible arguments, fields and enum values on a field you added to a query.

.. code-block:: python

    q = Query.region("01")
    stat = q.add_field("BEV001")
    stat.get_info()

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
