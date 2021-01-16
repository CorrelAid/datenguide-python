============
Helper Functions
============
The package provides three helper functions to provide
the user with information about regions, statistics
and the availability of data for region-statistic
combinations. Helper functions are part of the
``datenguidepy.query_helper`` module but can also be imported
from ``datenguidepy`` directly.

**get_statistics**
- List the statstic codes available in the API
- Gives a short and long description for the corresponding statistic
- Default description language is German
- Provides a machine translated version of the descriptions in english

**get_regions**
- Lists the region ids used to construct queries
- Contains a human readable name of the region
- Contains the european statistical calssfication of the region (nuts/lau)
- Contains the id of the parent region

**get_availability_summary**
- Lists all combination of statsitics with regions down to nuts 3 level.
- For each combination provids the size of the corresponding data set
- For each combination prvides the first and the last year of available data
- Does not include lau regions
- Does not include information about ENUMs
