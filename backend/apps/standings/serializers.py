from rest_framework import serializers

from apps.core.serializers import SeasonWeekQuerySerializer
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
            "point_differential",
            "streak",
        ]


class LeagueStandingsQuerySerializer(SeasonWeekQuerySerializer):
    pass


class ConferenceStandingsQuerySerializer(LeagueStandingsQuerySerializer):
    conference = serializers.ChoiceField(required=True, choices=Conferences.choices)

    def validate(self, data):
        return data


class DivisionStandingsQuerySerializer(LeagueStandingsQuerySerializer):
    division = serializers.ChoiceField(required=True, choices=Divisions.choices)

    def validate(self, data):
        return data