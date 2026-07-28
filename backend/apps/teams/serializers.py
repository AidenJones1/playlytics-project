from rest_framework import serializers

from apps.teams.models import Team

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            'abbreviation',
            'logo',
            'color_1',
            'color_2',
            'color_3',
            'color_4',
        ]

class TeamDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"