=============
Data Pitfalls
=============


Multiple sources for one statistic
----------------------------------

.. code-block:: python

    from datenguidepy import Query
    
    q = Query.region('01')
    q.add_field('BEVSTD')
    result_df = q.results()
    
    
====  ====  ==================  ======  ========  ==========================================  ==========================  ===========================  ====================  ===================
  ..    id  name                  year    BEVSTD  BEVSTD_source_title_de                      BEVSTD_source_valid_from    BEVSTD_source_periodicity      BEVSTD_source_name  BEVSTD_source_url
====  ====  ==================  ======  ========  ==========================================  ==========================  ===========================  ====================  ===================
   0    01  Schleswig-Holstein    1995   2725461  Fortschreibung des Bevölkerungsstandes      1995-12-31T00:00:00         JAEHRLICH                                   12411
   1    01  Schleswig-Holstein    1996   2742293  Fortschreibung des Bevölkerungsstandes      1995-12-31T00:00:00         JAEHRLICH                                   12411
   2    01  Schleswig-Holstein    1997   2756473  Fortschreibung des Bevölkerungsstandes      1995-12-31T00:00:00         JAEHRLICH                                   12411
   3    01  Schleswig-Holstein    1998   2766057  Erhebung der öffentlichen Wasserversorgung  1998-01-01T00:00:00         JAEHRLICH                                   32211
   4    01  Schleswig-Holstein    1998   2766057  Fortschreibung des Bevölkerungsstandes      1995-12-31T00:00:00         JAEHRLICH                                   12411
====  ====  ==================  ======  ========  ==========================================  ==========================  ===========================  ====================  ===================

Changing region ids
-------------------

.. code-block:: python

    from datenguidepy import Query
    
    q = Query.region('01')
    q.add_field('BEVSTD')
    result_df = q.results()