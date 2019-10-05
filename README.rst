=================
Datenguide Python
=================


.. image:: https://img.shields.io/pypi/v/datenguide_python.svg
        :target: https://pypi.python.org/pypi/datenguide_python

.. image:: https://img.shields.io/travis/AlexandraKapp/datenguide_python.svg
        :target: https://travis-ci.org/AlexandraKapp/datenguide_python

.. image:: https://readthedocs.org/projects/datenguide-python/badge/?version=latest
        :target: https://datenguide-python.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Python Wrapper for the Datenguide API.


* Free software: MIT license
* Documentation: https://datenguide-python.readthedocs.io.


Features
--------

### A python package to easily retreive data from [Regionalstatistik](https://www.regionalstatistik.de/genesis/online/logon) via the [Datenguide API](https://github.com/datenguide/datenguide-api). 

To use the package install the package with 
```
pip install xxx
```

Import the package into your file
```python
from xx import Query
```

## Creating a query
```python
# either for single regions
query_singleregion = Query.region('01')

# or for all subregions a a region (e.g. all Kommunen in a Bundeland)
query = Query.allRegions(parent='01')
```

Add statistics you want to get data one
```python
query.add_field('BEV001')
```

A field can also be added with filters. E.g. you can specify, that only data from a specific year shall be returned.
```python
query.add_field('BEV001', args={year:'2017'})
```

A set of default fields is defined (year, value, source). If additional fields shall be returned, they can be specified as a field argument.
`
query.add_field('BEV001', field=['GES'])
`


Get the results as a Pandas DataFrame

```python
df = query.results()
```

## Get information on fields and meta data

# TODO

## Further information

for detailed examples see the notebooks xxx.

For a detailled documentation of all statistics and fields see the Datenguide API.


Credits
-------

This package is using the Datenguide API to retrieve information of Regionalstatistik.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
