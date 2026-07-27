from rest_framework import serializers

from apps.core import serializers as cs
from apps.core.validators import does_team_exist
from apps.elo_ratings.services import ratings
from apps.scheduling.models import Game
from apps.standings.services import rankings
from apps.stats.services import stats
from apps.teams.serializers import TeamSerializer


class WeeklyScheduleSerializer(cs.BaseScheduleSerializer):
    home_team = serializers.SerializerMethodField()
    away_team = serializers.SerializerMethodField()

    class Meta(cs.BaseScheduleSerializer.Meta):
        model = Game
        fields = cs.BaseScheduleSerializer.Meta.fields

    def get_home_team(self, obj):
        data = dict(TeamSerializer(obj.home_team).data)
        data["ratings"] = ratings.get_pregame_ratings_for_team(obj.home_team, obj)
        return data

    def get_away_team(self, obj):
        data = dict(TeamSerializer(obj.away_team).data)
        data["ratings"] = ratings.get_pregame_ratings_for_team(obj.away_team, obj)
        return data


class GamePreviewSerializer(cs.BaseScheduleSerializer):
    home_team = serializers.SerializerMethodField()
    away_team = serializers.SerializerMethodField()

    class Meta(cs.BaseScheduleSerializer.Meta):
        model = Game
        fields = cs.BaseScheduleSerializer.Meta.fields + [
            "venue",
        ]

    def get_home_team(self, obj):
        data = dict(TeamSerializer(obj.home_team).data)
        data["ratings"] = ratings.get_pregame_ratings_for_team(obj.home_team, obj)
        data["rankings"] = rankings.get_team_pregame_rankings(obj, obj.home_team)
        seasonal_stats = stats.get_team_seasonal_stats(obj.home_team, obj)
        data["seasonal_stats"] = seasonal_stats
        rolling_stats = stats.get_team_rolling_stats(obj.home_team, obj, window=5)
        data["rolling_stats"] = rolling_stats
        return data

    def get_away_team(self, obj):
        data = dict(TeamSerializer(obj.away_team).data)
        data["ratings"] = ratings.get_pregame_ratings_for_team(obj.away_team, obj)
        data["rankings"] = rankings.get_team_pregame_rankings(obj, obj.away_team)
        seasonal_stats = stats.get_team_seasonal_stats(obj.away_team, obj)
        data["seasonal_stats"] = seasonal_stats
        rolling_stats = stats.get_team_rolling_stats(obj.away_team, obj, window=5)
        data["rolling_stats"] = rolling_stats
        return data

    
class GameResultsSerializer(cs.BaseScheduleSerializer):
    home_team = serializers.SerializerMethodField()
    away_team = serializers.SerializerMethodField()

    class Meta(cs.BaseScheduleSerializer.Meta):
        model = Game
        fields = cs.BaseScheduleSerializer.Meta.fields + [
            "venue",
        ]

    def get_home_team(self, obj):
        data = dict(TeamSerializer(obj.home_team).data)
        data["ratings"] = ratings.get_postgame_ratings_for_team(obj.home_team, obj)
        data["rankings"] = rankings.get_team_pregame_rankings(obj, obj.home_team)
        data["game_stats"] = stats.get_game_stats_for_team(obj.home_team, obj)
        return data

    def get_away_team(self, obj):
        data = dict(TeamSerializer(obj.away_team).data)
        data["ratings"] = ratings.get_postgame_ratings_for_team(obj.away_team, obj)
        data["rankings"] = rankings.get_team_pregame_rankings(obj, obj.away_team)
        data["game_stats"] = stats.get_game_stats_for_team(obj.away_team, obj)
        return data


class WeeklyScheduleQuerySerializer(cs.SeasonWeekQuerySerializer, cs.DivisionConferenceQuerySerializer):
    pass


class TeamScheduleQuerySerializer(cs.SeasonQuerySerializer, cs.DivisionConferenceQuerySerializer):
    team = serializers.CharField(required=True, allow_blank=False, max_length=5)

    def validate_team(self, value):
        does_team_exist(value)
        return value

    def validate(self, data):
        return super().validate(data)