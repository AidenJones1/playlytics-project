from rest_framework import serializers

from apps.core import constants
from apps.core.serializers import SeasonWeekQuerySerializer
from apps.core.utils import dates

class OffenseStatsSerializer(serializers.Serializer):
    games_played = serializers.IntegerField()
    total_rushing_attempts = serializers.IntegerField()
    total_rushing_yards = serializers.IntegerField()
    total_passing_attempts = serializers.IntegerField()
    total_completed_passes = serializers.IntegerField()
    total_passing_yards = serializers.IntegerField()
    total_rushing_touchdowns = serializers.IntegerField()
    total_passing_touchdowns = serializers.IntegerField()
    total_touchdowns = serializers.IntegerField()
    total_sacks_allowed = serializers.IntegerField()
    total_interceptions_thrown = serializers.IntegerField()
    total_fumbles_lost = serializers.IntegerField()
    total_turnovers_given = serializers.IntegerField()
    total_successful_plays = serializers.IntegerField()

class DefenseStatsSerializer(serializers.Serializer):
    games_played = serializers.IntegerField()
    rushes_defended = serializers.IntegerField()
    rushing_yards_allowed = serializers.IntegerField()
    passes_defended = serializers.IntegerField()
    completions_allowed = serializers.IntegerField()
    passing_yards_allowed = serializers.IntegerField()
    rushing_touchdowns_allowed = serializers.IntegerField()
    passing_touchdowns_allowed = serializers.IntegerField()
    total_touchdowns_allowed = serializers.IntegerField()
    sacks_made = serializers.IntegerField()
    interceptions_made = serializers.IntegerField()
    fumbles_taken = serializers.IntegerField()
    total_turnovers_taken = serializers.IntegerField()
    total_successful_plays_allowed = serializers.IntegerField()


class SeasonStatsQuerySerializer(SeasonWeekQuerySerializer):
    week = serializers.IntegerField(
        default=dates.get_current_week_number_exclude_playoffs,
        min_value=constants.MIN_WEEK_NUMBER,
        max_value=constants.MAX_WEEK_NUMBER,
    )
    side = serializers.ChoiceField(required=True, choices=["offense", "defense"])