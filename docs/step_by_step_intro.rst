============
Setup query
============
Within your python file or notebook:

**1. Import the package**

.. code-block:: python

    from datenguidepy import Query
    from datenguidepy import get_regions
    from datenguidepy import get_statistics

**2. Creating a query**

Start with querying either for single regions:

.. code-block:: python

    q = Query.region('01')

or for all subregions within a region (e.g. all Kommunen in a Bundesland)

.. code-block:: python

   query_allregions = Query.all_regions(parent='01')

- How to get IDs for regions?

.. code-block:: python

    # Overview of region IDs
    get_regions()

Use pandas *query()* functionality to filter according to level, e.g. for Bundesländer *"nuts1"*

.. code-block:: python

    # Filtered for Bundesländer (federal states)
    get_regions().query("level == 'nuts1'")

See below "Get information on fields and meta data" for more options on regions.

**3. Add statistics (fields)**

Add statistics to your query for which you want to get data

.. code-block:: python

    stats = q.add_field('BEV001')

- How do I find the short name of the statistics?

.. code-block:: python

    # Some examples
    TOPIC: Economy
     - Bruttoinlandsprodukt (BIP802)
     - Verarbeitendes Gewerbe Betriebe (BETR01)
     - Verarbeitendes Gewerbe Umsatz (UMS002)
     - Bevölkerungsstand (BEVSTD)
     - Beschäftigte (ERW012)
     - Arbeitslose (ERWP06)

     TOPIC: Demographic Development
     - Bevölkerungsstand (BEVSTD)
     - Lebendgeborene (BEV001)
     - Gestorbene (BEV002)
     - Eheschließungen (BEV003)
     - Ehescheidungen (BEV004)
     - Zuzüge, Wanderungen über die Kreisgrenzen (BEV085)
     - Fortzüge, Wanderungen über die Kreisgrenzen (BEV086)

See below "Get information on fields and meta data" for more options on statistics.

**4. Get results**

Get the results as a Pandas DataFrame

.. code-block:: python

    df = q.results()

===================
Additional Features
===================

**5. Add filters and subfields**

Filters can be added to statistics (fields) to select data only from specific years.

.. code-block:: python

    stats.add_args({'year': [2014, 2015]})

**5.1. Add subfield**
A set of default subfields (year, value, source) are defined for all statistics. 
If additional fields (columns in the results table) shall be returned, they can be specified as a field argument.

.. code-block:: python

    stats.add_field('GES') # Geschlecht

    # by default the summed value for a field is returned. 
    # E.g. if the field "Geschlecht" is added, the results table will show "None" in each row, 
    # which means total value for women and man.
    # To get disaggregated values, they speficically need to be passed as args. 
    # If e.g. only values for women shall be returned, use:

    stats.add_args({'GES': 'GESW'})

    # if all possible enum values shall be returned disaggregated, pass 'ALL':

    stats.add_args({'GES': 'ALL'})

**6. Get results**
Again, results can be returned as a Pandas DataFrame

.. code-block:: python

    df2 = q.results()
