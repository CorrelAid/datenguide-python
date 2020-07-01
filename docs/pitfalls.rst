=============
Data Pitfalls
=============


Multiple sources for one statistic
----------------------------------

Consider the followin query without source information.

.. code-block:: python

    from datenguidepy import Query
    
    q = Query.region('01')
    q.add_field('BEVSTD')
    result_df = q.results()
    result_df.head().iloc[:,:4]
    
    
====  ====  ==================  ======  ========
  ..    id  name                  year    BEVSTD
====  ====  ==================  ======  ========
   0    01  Schleswig-Holstein    1995   2725461
   1    01  Schleswig-Holstein    1996   2742293
   2    01  Schleswig-Holstein    1997   2756473
   3    01  Schleswig-Holstein    1998   2766057
   4    01  Schleswig-Holstein    1998   2766057
====  ====  ==================  ======  ========

As can be seen in the results the value for 1998 appears twice.
The reason is that the values come from different sources. This
is the reason why sources are part of the results by default.
When one encounters unexpected values it is a good idea to check
sources for uniqueness.

It is also important to not that different sources may actually
report different values for the same year, unlike the example
above.



Changing region ids
-------------------

Sometmes region ids change at a point in time without
an apparent reason. For example when looking for an id
for the small town Binz one finds two distinct ids.

.. code-block:: python

    from datenguidepy import get_regions
    
    reg = get_regions()
    reg[reg.name.str.contains('Binz',case=False)]
    
===========  ======  =======  ========
  region_id  name    level      parten
===========  ======  =======  ========
   13061005  Binz    lau         13061
   13073011  Binz    lau         13073
   08336008  Binzen  lau         08336
===========  ======  =======  ========

If one uses these ids to query data one id will deliver data until 2010
and the other starting from 2011. The reason is an administrative
change on the county level (nuts3), which is one level higher
in the region hierarchy. Looking at the parents for the above results
one finds the following.
    
.. code-block:: python

    reg[(reg.index == '13061') | (reg.index == '13073')]
    
===========  ==========================  =======  =========
  region_id  name                        level      partent
===========  ==========================  =======  =========
      13061  Landkreis Rügen             nuts3          130
      13073  Landkreis Vorpommern-Rügen  nuts3          130
===========  ==========================  =======  =========
    
This reflects the administrative change that happened in 2011. On
the county level. Because region ids reflect the hierarchy reflect
the region hierarchy such a change causes all subregions to get new
ids. Therefore Binz appears twice in the list of all regions.

Most of the time such a situation can be resolved with the help
of the region name. But sometimes it might be a little more
difficuilt if the id change coincides with a slight name change.