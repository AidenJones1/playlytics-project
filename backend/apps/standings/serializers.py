from rest_framework import serializers

from apps.core import constants
from apps.core.serializers import SeasonWeekQuerySerializer
from apps.core.utils import dates
from apps.scheduling.choices import SeasonType
from apps.scheduling.models import Week
from apps.standings.models import TeamStandings
from apps.teams.choices import Conferences, Divisions
from apps.teams.serializers import TeamSerializer

class StandingsSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = TeamStandings
        fields = [
            "team",
            "wins",
            "losses",
            "ties",
            "percentage",
            "home_wins",
            "home_losses",
            "home_ties",
            "away_wins",
            "away_losses",
            "away_ties",
            "conference_wins",
            "conference_losses",
            "conference_ties",
            "division_wins",
            "division_losses",
            "division_ties",
            "points_for",
            "points_against",
            "point_differential",
            "streak",
        ]


class LeagueStandingsQuerySerializer(SeasonWeekQuerySerializer):
    week = serializers.IntegerField(
        default=dates.get_current_week_number_exclude_playoffs,
        min_value=constants.MIN_WEEK_NUMBER,
        max_value=constants.MAX_WEEK_NUMBER,
    )


class ConferenceStandingsQuerySerializer(LeagueStandingsQuerySerializer):
    conference = serializers.ChoiceField(required=True, choices=Conferences.choices)

    def validate(self, data):
        return data


class DivisionStandingsQuerySerializer(LeagueStandingsQuerySerializer):
    division = serializers.ChoiceField(required=True, choices=Divisions.choices)

    def validate(self, data):
        return data