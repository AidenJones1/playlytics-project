from rest_framework import serializers

from apps.core import constants
from apps.core.utils import dates
from apps.scheduling.models import Game
from apps.teams.choices import Conferences, Divisions
from apps.teams.serializers import TeamSerializer

class BaseScheduleSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField(read_only=True, source='week.season.year')
    week = serializers.IntegerField(read_only=True, source='week.week')
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)

    class Meta:
        model = Game
        fields = [
            "id",
            "year",
            "week",
            "game_time",
            "status",
            "away_team",
            "away_score",
            "home_team",
            "home_score",
        ]


class SeasonQuerySerializer(serializers.Serializer):
    season = serializers.IntegerField(
        default=dates.get_current_season_year,
        min_value=constants.MIN_SEASON_YEAR,
        max_value=constants.MAX_SEASON_YEAR
    )


class SeasonWeekQuerySerializer(SeasonQuerySerializer):
    week = serializers.IntegerField(
        default=dates.get_current_week_number,
        min_value=constants.MIN_WEEK_NUMBER,
        max_value=constants.MAX_WEEK_NUMBER
    )


class ConferenceQuerySerializer(serializers.Serializer):
    conference = serializers.ChoiceField(
        choices=Conferences.choices,
        required=False
    )


class DivisionQuerySerializer(serializers.Serializer):
    division = serializers.ChoiceField(
        choices=Divisions.choices,
        required=False
    )


class DivisionConferenceQuerySerializer(ConferenceQuerySerializer, DivisionQuerySerializer):
    pass