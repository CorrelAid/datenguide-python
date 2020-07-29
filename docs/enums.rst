===========
Dimension/Enums
===========

Some statistics are available on a more granular level. This is sometimes
referred to as curring the data among additional dimensions or as **splitting
it according to enums**. This package sticks to the latter.

An enumeration, or enum, "is a a set of symbolic names (members) bound to unique,
 constant values" ([python enums](https://docs.python.org/3/library/enum.html)).
It is stricter than a dictionary as it ensures e.g. uniquness.

In order to extract more granular data one needs to add two lines to the what
constitutes a minimal example.

.. code-block:: python

    from datenguidepy.query_builder import Query

    q = Query.region('01')
    stat = q.add_field('BEVSTD')
    stat.add_field('GES') # add gender column to the output
    stat.add_args({'GES':'ALL'}) # request all genders (pluts total)
    q.results().head(6).iloc[:,:5]

====  ==================  =====  ======  ========
  id  name                GES      year    BEVSTD
====  ==================  =====  ======  ========
  01  Schleswig-Holstein  GESM     1995   1330257
  01  Schleswig-Holstein  GESW     1995   1395204
  01  Schleswig-Holstein           1995   2725461
  01  Schleswig-Holstein  GESM     1996   1339326
  01  Schleswig-Holstein  GESW     1996   1402967
  01  Schleswig-Holstein           1996   2742293
====  ==================  =====  ======  ========
    
The first added line only causes the gender information to be added to the output.
This would affect the results by itself, because the package always provides totals
accross the enums by default. The Second line changes that and tells `pydatenguide`
to request all differnt gender data individually in addition to the total. 
This line by itself would also not suffice, as the user could not distinguish the
different results without adding the gender column:

.. code-block:: python

    from datenguidepy.query_builder import Query

    q = Query.region('01')
    stat = q.add_field('BEVSTD')
    # comment out adding the enums:
    # stat.add_field('GES') # add gender column to the output
    stat.add_args({'GES':'ALL'}) # request all genders (pluts total)
    q.results().head(6).iloc[:,:5]

====  ==================  ======  ========  ======================================
  id  name                  year    BEVSTD  BEVSTD_source_title_de
====  ==================  ======  ========  ======================================
  01  Schleswig-Holstein    1995   1330257  Fortschreibung des Bevölkerungsstandes
  01  Schleswig-Holstein    1995   1395204  Fortschreibung des Bevölkerungsstandes
  01  Schleswig-Holstein    1995   2725461  Fortschreibung des Bevölkerungsstandes
  01  Schleswig-Holstein    1996   1339326  Fortschreibung des Bevölkerungsstandes
  01  Schleswig-Holstein    1996   1402967  Fortschreibung des Bevölkerungsstandes
  01  Schleswig-Holstein    1996   2742293  Fortschreibung des Bevölkerungsstandes
====  ==================  ======  ========  ======================================


The ``'ALL'`` argument works for all enums and is usually the most convenient way to obtain
the information. Alternatively enum information can be requested specifically
by specifying the particular member of the enum. In the case of gender the members
are ``'GESM'`` and ``'GESW'``.

In order to figure out which enums exist for a particular statistic and which members they
have, the ``.get_info`` method can be used for the statistic. In this case that would mean calling
``stat.get_info()``, which will print detailed information about the statistic on the screen
inlcuding its enums. Note that enum names can be empty in the database, in case 
they are define but not populated.


``stat.get_info()`` returns (shortend):

.. code-block:: none
    :linenos:

    kind:
    OBJECT

    description:
    Bevölkerungsstand

    arguments:
    year: LIST of type SCALAR(Int)

    statistics: LIST of type ENUM(BEVSTDStatistics)
    enum values:
    R12411: Fortschreibung des Bevölkerungsstandes
    R32211: Erhebung der öffentlichen Wasserversorgung

    ALTX75: LIST of type ENUM(ALTX75)
    enum values:
    ALT000: unter 1 Jahr
    ...
    ALT085UM: 85 Jahre und mehr
    GESAMT: Gesamt

    GES: LIST of type ENUM(GES)
    enum values:
    GESM: männlich
    GESW: weiblich
    GESAMT: Gesamt

    ALTX21: LIST of type ENUM(ALTX21)
    enum values:
    ALT000B03: unter 3 Jahre
    ...
    ALT090UM: 90 Jahre und mehr
    GESAMT: Gesamt

    NAT: LIST of type ENUM(NAT)
    enum values:
    NATA: Ausländer(innen)
    NATD: Deutsche
    GESAMT: Gesamt

    ALTX76: LIST of type ENUM(ALTX76)
    enum values:
    ALT000: unter 1 Jahr
    ...
    ALT090UM: 90 Jahre und mehr
    GESAMT: Gesamt

    ALTX20: LIST of type ENUM(ALTX20)
    enum values:
    ALT000B03: unter 3 Jahre
    ...
    ALT075UM: 75 Jahre und mehr
    GESAMT: Gesamt

    filter: INPUT_OBJECT(BEVSTDFilter)

    fields:
    id: Interne eindeutige ID
    year: Jahr des Stichtages
    value: Wert
    source: Quellenverweis zur GENESIS Regionaldatenbank
    ALTX75: Altersjahre (unter 1 bis 75, Altersgruppen)
    GES: Geschlecht
    ALTX21: Altersgruppen (unter 3, 5er-Schritte, 90 und mehr)
    NAT: Nationalität
    ALTX76: Altersjahre (unter 1 bis 90, Altersgruppen)
    ALTX20: Altersgruppen (unter 3 bis 75 u. m.)

    enum values:
    None


See line 22-26 for our previous discussed example. 

One last variation to summarize of our example:

from datenguidepy.query_builder import Query

.. code-block:: python
    q = Query.region('01')
    stat = q.add_field('BEVSTD')
    stat.add_field('GES') # add gender column to the output
    stat.add_args({'GES':'GESAMT'}) # request all genders (pluts total)
    df_head = q.results().head(6).iloc[:,:5]
    df_head

====  ==================  ======  ======  ========
  id  name                GES       year    BEVSTD
====  ==================  ======  ======  ========
  01  Schleswig-Holstein  GESAMT    1995   2725461
  01  Schleswig-Holstein  GESAMT    1996   2742293
  01  Schleswig-Holstein  GESAMT    1997   2756473
  01  Schleswig-Holstein  GESAMT    1998   2766057
  01  Schleswig-Holstein  GESAMT    1998   2766057
  01  Schleswig-Holstein  GESAMT    1999   2777275
====  ==================  ======  ======  ========