=======
History
=======

0.1.0 (2019-10-07)
------------------

* First release on PyPI.

0.1.1 (2019-10-09)
------------------

* Cleanup of the first release regarding naming, authors and docs.

0.2.0 (2020-11-30)
------------------

* Added functionality to use meta data for displaying descriptive statistics names and enum values

0.2.1 (2020-05-17)
------------------
* Added functionality to display the units of a statistic along with the numerical value.
* Internally split the meta data extraction into technical meta data and meta data about the statistics. Implemented new defaults for the statistics meta data in order to account for changes in the datenguide API.

0.2.2 (2020-05-24)
------------------
* Fixed a critical bug in the package data perventing the pypi version to essentially stop working completely.
* Fixed a bug related to incorrectly displayed version number of the package.

0.3.0 (2020-06-24)
------------------
* renamed get_all_regions to get_regions in accordance with get_statistics 
* changed the index column name of the DataFrame returnd by all_regions from id to region_id
* made the statstics column name the index in the DataFrame returned by get_statistics and renamed it to statistic
* added functionality to obtain a stored auto-translated version of the get_statistics descriptions (default is German, now machine translation is available in English)
* introduced a new helper function get_availability_summary containing a (pre-calculated) summary of available data for region_id, statistic pairs down to nut3 level.

0.3.1 (2020-07-14)
------------------
* Introduced a better error messages for queries that are run without a statistic
* Bug fixes related to enums and auto join functionality

0.4.0 (2021-01-23)
------------------
* Introduced better error messages in case of invalid regions
* Introduced duplicate removal as an option for standard query results
  * New default is to remove duplicates but can be turned of with an argument
  * Auto-joining of multiple statistics should work better now as duplicates are removed before the joining.
  * Purpouse is only to remove duplicates that that may exist for technichal API reasons. The Purpouse is not to filter the data for content.
  * Rows are only counted as duplaces if everything, including the data source is identical
