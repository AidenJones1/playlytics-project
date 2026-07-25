from rest_framework import serializers

from apps.core import serializers as cs
from apps.core.validators import does_team_exist
from apps.scheduling.models import Game

class WeeklyScheduleSerializer(cs.BaseScheduleSerializer):
    class Meta(cs.BaseScheduleSerializer.Meta):
        model = Game
        fields = cs.BaseScheduleSerializer.Meta.fields


class GamePreviewSerializer(cs.BaseScheduleSerializer):
    class Meta(cs.BaseScheduleSerializer.Meta):
        model = Game
        fields = cs.BaseScheduleSerializer.Meta.fields + [
            "venue",
        ]


class GameResultsSerializer(cs.BaseScheduleSerializer):
    class Meta(cs.BaseScheduleSerializer.Meta):
        model = Game
        fields = cs.BaseScheduleSerializer.Meta.fields + [
            "venue",
        ]


class WeeklyScheduleQuerySerializer(cs.SeasonWeekQuerySerializer, cs.DivisionConferenceQuerySerializer):
    pass


class TeamScheduleQuerySerializer(cs.SeasonQuerySerializer, cs.DivisionConferenceQuerySerializer):
    team = serializers.CharField(required=True, allow_blank=False, max_length=5)

    def validate_team(self, value):
        does_team_exist(value)
        return value

    def validate(self, data):
        return super().validate(data)