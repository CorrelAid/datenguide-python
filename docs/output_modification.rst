============
Enhanced Output 
============

In order to help users to better use and understand the results of a query there are a few flags
that can be set to increase the readability of the output. All these enhancements are turned off
by default, as the make the output harder to handle from a technichal point of view and don't
add too much value for statistics with which the user is already familar. When exploring the
data on the other hand it is highly recommended to take advantage of this functionality.

**Statistic codes**

.. code-block:: python

    q = Query.region('01')
    stat = q.add_field('BEVSTD')
    q.results(verbose_statistics = False).head(5).iloc[:,:4]

====  ====  ==================  ======  ========
  ..    id  name                  year    BEVSTD
====  ====  ==================  ======  ========
   0    01  Schleswig-Holstein    1995   2725461
   1    01  Schleswig-Holstein    1996   2742293
   2    01  Schleswig-Holstein    1997   2756473
   3    01  Schleswig-Holstein    1998   2766057
====  ====  ==================  ======  ========

.. code-block:: python

    q = Query.region('01')
    stat = q.add_field('BEVSTD')
    q.results(verbose_statistics = True).head(5).iloc[:,:4]
    
====  ====  ==================  ======  ============================
  ..    id  name                  year    Bevölkerungsstand (BEVSTD)
====  ====  ==================  ======  ============================
   0    01  Schleswig-Holstein    1995                       2725461
   1    01  Schleswig-Holstein    1996                       2742293
   2    01  Schleswig-Holstein    1997                       2756473
   3    01  Schleswig-Holstein    1998                       2766057
====  ====  ==================  ======  ============================


**Enum codes**

.. code-block:: python

    q = Query.region('01')
    stat = q.add_field('BEVSTD')
    stat.add_field('GES')
    stat.add_args({'GES':'ALL'})
    q.results(verbose_enums=False).head(6).iloc[:,:5]
    
====  ====  ==================  =====  ======  ========
  ..    id  name                GES      year    BEVSTD
====  ====  ==================  =====  ======  ========
   0    01  Schleswig-Holstein  GESM     1995   1330257
   1    01  Schleswig-Holstein  GESW     1995   1395204
   2    01  Schleswig-Holstein  None     1995   2725461
   3    01  Schleswig-Holstein  GESM     1996   1339326
====  ====  ==================  =====  ======  ========

    
.. code-block:: python

    q = Query.region('01')
    stat = q.add_field('BEVSTD')
    stat.add_field('GES')
    stat.add_args({'GES':'ALL'})
    q.results(verbose_enums=True).head(6).iloc[:,:5]
    
====  ====  ==================  ========  ======  ========
  ..    id  name                GES         year    BEVSTD
====  ====  ==================  ========  ======  ========
   0    01  Schleswig-Holstein  männlich    1995   1330257
   1    01  Schleswig-Holstein  weiblich    1995   1395204
   2    01  Schleswig-Holstein  Gesamt      1995   2725461
   3    01  Schleswig-Holstein  männlich    1996   1339326
====  ====  ==================  ========  ======  ========

 
**Statistic Units**

An additional column per statistic can be added containing
the unit of that statsitic. This might be needed to put
fully understand the numbers. In the example of a ground
area statistic the unit is hectare (ha).


.. code-block:: python

    q = Query.region('01')
    stat = q.add_field('FLCX05')
    q.results(add_units = True).head(5).iloc[:,:5]

====  ====  ==================  ======  ========  =============
  ..    id  name                  year    FLCX05  FLCX05_unit
====  ====  ==================  ======  ========  =============
   0    01  Schleswig-Holstein    1996   1577055  ha
   1    01  Schleswig-Holstein    2000   1576297  ha
   2    01  Schleswig-Holstein    2004   1576329  ha
   3    01  Schleswig-Holstein    2008   1579919  ha
   4    01  Schleswig-Holstein    2009   1579907  ha
====  ====  ==================  ======  ========  =============

At the moment units are only available in German. Many of them
are language independent abriviations anyways, but some are
actual words, like the german word for count (Anzahl).
