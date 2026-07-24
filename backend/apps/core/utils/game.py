from apps.scheduling.choices import GameLocation

def get_game_location(location_str):
    """Convert a game location string to a GameLocation enum."""
    if location_str == "Home":
        return GameLocation.HOME
    elif location_str == "Away":
        return GameLocation.AWAY
    elif location_str == "Neutral":
        return GameLocation.NEUTRAL
    return None