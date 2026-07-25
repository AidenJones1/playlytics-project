from datetime import datetime

from django.utils import timezone

from apps.core import constants
from apps.scheduling.choices import SeasonType
from apps.scheduling.models import Season, Week

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

def get_current_season_year():
    """Get the current season year based on the current date."""
    now = timezone.now().date()

    # 1) If today is within any season window (regular or playoffs), return that season year.
    active_season_obj = Season.objects.filter(
        start_date__lte=now,
        end_date__gte=now,
    ).order_by('-year', '-start_date').first()

    if active_season_obj:
        return active_season_obj.year

    # 2) If today is before the start of the latest season, return the previous season year.
    latest_season_obj = Season.objects.order_by('-year', '-start_date').first()
    if not latest_season_obj:
        return constants.DEFAULT_SEASON

    if now < latest_season_obj.start_date:
        return latest_season_obj.year - 1
    return latest_season_obj.year


def get_current_week_number():
    """Get the current week number using the latest season and date-based fallbacks."""
    now = timezone.now().date()
    latest_season_obj = Season.objects.order_by('-year', '-start_date').first()
    if not latest_season_obj:
        return constants.DEFAULT_WEEK

    season_week_objs = Week.objects.filter(season=latest_season_obj).order_by('start_date', 'week')
    first_week_obj = season_week_objs.first()
    latest_week_obj = season_week_objs.order_by('-end_date', '-week').first()

    if not first_week_obj or not latest_week_obj:
        return constants.DEFAULT_WEEK

    # If today is before the first week starts, return week 1.
    if now < first_week_obj.start_date:
        return 1

    # If today is after the last available week ends, return the last available week number.
    if now > latest_week_obj.end_date:
        return latest_week_obj.week

    # If today falls inside a week window, return that week.
    week_obj = season_week_objs.filter(start_date__lte=now, end_date__gte=now).order_by('week').first()
    if week_obj:
        return week_obj.week

    return constants.DEFAULT_WEEK