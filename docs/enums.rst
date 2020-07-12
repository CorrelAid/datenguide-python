===========
Dimension/Enums
===========

Some statistics are available on a more granular level which is sumtimes
referred to as curring the data among additional dimensions or as splitting
it according to enums. This package sticks to the latter.

In order to extract more granular data one needs to add two lines to the what
constitutes a minimal example.

.. code-block:: python

    from datenguidpy.query_builder import Query

    q = Query.region('01')
    stat = q.add_field('BEVSTD')
    stat.add_field('GES') # add gender column to the output
    stat.add_args({'GES':'ALL'}) # request all genders (pluts total)
    q.results().head(6).iloc[:,:5]
    
The first added line only causes the gender information to be added to the output.
This would affect the results by itself, because the package always proveds totals
accross the enums by default. The Second line changes that and tells the package
to request all differnt gender data individually in addition to the total.
This line by itself would also not suffice, as the use could not distinguish the
different results without adding the gender column.

The ``'ALL'`` argument works for all enums and is usually the most convenient way to obtain
the information. Alternatively enum information can be requested specifically
by specifying the particular member of the enum. In the case of gener the members
are ``'GESM'`` and ``'GESW'``.

In order to figure out which enums exist for a particular statistic and which members they
have, the ``.get_info`` method can be used. For the statistic. In this case that would mean calling
``stat.get_info()``, which will print detailed information about the statistic on the screen
inlcuding its enums.