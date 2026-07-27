from rest_framework import serializers

from apps.elo_ratings.models import TeamELORating
from apps.teams.serializers import TeamSerializer

class TeamELORatingSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = TeamELORating
        fields = [
            "team",
            "ratings_before",
            "ratings_after",
            "gained",
            "average_opponent_ratings",
            "highest_ratings",
            "lowest_ratings",
            "average_gain",
        ]