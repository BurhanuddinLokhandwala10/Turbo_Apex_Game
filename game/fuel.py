"""
Fuel Management & Pickup Respawner
==================================
Manages fuel replenishment cycles and canister respawn timers.
"""

class FuelManager:
    """Manages world fuel canister states."""

    @staticmethod
    def update_pickups(fuel_pickups, dt):
        """Updates canister respawn timers so pickups can be re-collected."""
        for pickup in fuel_pickups:
            if pickup["collected"]:
                pickup["respawn_timer"] -= dt
                if pickup["respawn_timer"] <= 0.0:
                    pickup["collected"] = False
                    pickup["respawn_timer"] = 0.0
