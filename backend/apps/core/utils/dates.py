from apps.core import constants
from apps.scheduling.choices import SeasonType

from datetime import datetime

def to_date_object(date_str):
    """Convert string formatted date to a date object."""
    if date_str is None:
        return None
    if isinstance(date_str, str):
        return datetime.strptime(date_str.split(" ")[0], "%Y-%m-%d").date()
    
def to_time_object(time_str):
    """Convert string formatted time to a time object."""
    if time_str is None:
        return None
    if isinstance(time_str, str):
        try:
            return datetime.strptime(time_str.strip(), "%H:%M").time()
        except ValueError:
            return None
    return None

def get_season_type(season_type_str):
    """Convert a season type string to a SeasonType enum."""
    if season_type_str in constants.REGULAR_SEASON_TYPES:
        return SeasonType.REGULAR
    elif season_type_str in constants.PLAYOFFS_SEASON_TYPES:
        return SeasonType.PLAYOFFS
    return None