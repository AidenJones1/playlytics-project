from rest_framework import serializers

from apps.core import serializers as cs
from apps.models.mixins import ModelPredictionMixin
from apps.scheduling.models import Game
from apps.elo_ratings.services import ratings
from apps.standings.services import rankings
from apps.stats.services import stats
from apps.teams.serializers import TeamSerializer

class GameOfTheWeekSerializer(ModelPredictionMixin, cs.BaseScheduleSerializer):
    home_team = serializers.SerializerMethodField()
    away_team = serializers.SerializerMethodField()
    model_prediction = serializers.SerializerMethodField()

    class Meta(cs.BaseScheduleSerializer.Meta):
        model = Game
        fields = cs.BaseScheduleSerializer.Meta.fields + [
            "venue",
            "model_prediction",
        ]

    def get_home_team(self, obj):
        data = dict(TeamSerializer(obj.home_team).data)
        data["ratings"] = ratings.get_pregame_ratings_for_team(obj.home_team, obj)
        data["rankings"] = rankings.get_team_pregame_rankings(obj, obj.home_team)
        return data

    def get_away_team(self, obj):
        data = dict(TeamSerializer(obj.away_team).data)
        data["ratings"] = ratings.get_pregame_ratings_for_team(obj.away_team, obj)
        data["rankings"] = rankings.get_team_pregame_rankings(obj, obj.away_team)
        return data