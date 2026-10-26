"""
Maps Package
============
Exports BeachMap, HillsMap, and CityMap.
"""

from maps.beach import BeachMap
from maps.hills import HillsMap
from maps.city import CityMap

MAP_CATALOG = [
    BeachMap,
    HillsMap,
    CityMap
]
