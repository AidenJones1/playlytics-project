from rest_framework import serializers

from apps.core import serializers as cs
from apps.scheduling.models import Game

class WeeklyScheduleSerializer(cs.BaseScheduleSerializer):
    class Meta(cs.BaseScheduleSerializer.Meta):
        model = Game
        fields = cs.BaseScheduleSerializer.Meta.fields

class WeeklyScheduleQuerySerializer(cs.SeasonWeekQuerySerializer, cs.DivisionConferenceQuerySerializer):
    pass