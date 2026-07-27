from rest_framework import serializers

from apps.core import constants
from apps.core.serializers import SeasonWeekQuerySerializer
from apps.core.utils import dates

class SeasonStatsQuerySerializer(SeasonWeekQuerySerializer):
    week = serializers.IntegerField(
        default=dates.get_current_week_number_exclude_playoffs,
        min_value=constants.MIN_WEEK_NUMBER,
        max_value=constants.MAX_WEEK_NUMBER,
    )
    side = serializers.ChoiceField(required=True, choices=["offense", "defense"])