"""
Track Management System
=======================
Wraps active map instance, tracks car segment spatial partitioning,
and provides fast spatial queries for collision and rendering.
"""

from maps.beach import BeachMap
from maps.hills import HillsMap
from maps.city import CityMap

class Track:
    """Encapsulates track layout and spatial partition of objects."""

    def __init__(self, map_type="BEACH"):
        self.map_type = map_type
        self.load_map(map_type)

    def load_map(self, map_type):
        """Loads and builds the selected race track."""
        self.map_type = map_type
        if map_type == "HILLS":
            self.map = HillsMap()
        elif map_type == "CITY":
            self.map = CityMap()
        else:
            self.map = BeachMap()

        self.segments = self.map.segments
        self.total_length = self.map.total_length
        self.total_segments = self.map.total_segments
        self.obstacles = self.map.obstacles
        self.fuel_pickups = self.map.fuel_pickups
        self.minimap_points = self.map.minimap_points
        self.palette = self.map.palette
        self.sky_surface = self.map.sky_surface

    def get_segment_at(self, z):
        """Returns the road segment at a given longitudinal world coordinate."""
        return self.map.get_segment_at(z)
