from rest_framework import serializers

from apps.core.validators import is_blacklisted
from apps.core.constants import MIN_SEASON_YEAR, MAX_SEASON_YEAR
from apps.pickems.models import PickemGroup, PickemGroupMember, UserPick, GamePickem
from apps.pickems.choices import PickemStatus
from apps.teams.models import Team
from apps.accounts.serializers import PublicAccountSerializer

class PickemsGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickemGroup
        fields = [
            'name',
            'is_private',
            'max_members',
            'created_at'
        ]

class PickemsGroupCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, min_length=3, max_length=255, validators=[is_blacklisted])
    is_private = serializers.BooleanField(default=True)
    max_members = serializers.IntegerField(default=10, min_value=2, max_value=16)

    def validate_max_members(self, value):
        group = self.instance
        if group and value < group.members.count():
            raise serializers.ValidationError("Max members cannot be less than the current number of members.")
        return value

    def validate(self, data):
        return data

class PickemsGroupJoinSerializer(serializers.Serializer):
    group_key = serializers.CharField(required=True, max_length=9)
    invite_code = serializers.CharField(required=False, max_length=12)

    def validate_group_key(self, value):
        group = PickemGroup.objects.filter(group_key=value).first()
        if not group:
            raise serializers.ValidationError("Invalid group key.")
        return value

    def validate(self, data):
        return data

class PickemsGroupMembershipSerializer(serializers.ModelSerializer):
    user = PublicAccountSerializer(read_only=True)

    class Meta:
        model = PickemGroupMember
        fields = [
            'user',
            'role'
        ]

class PickemsGroupOwnerSerializer(serializers.Serializer):
    user = serializers.CharField(required=True, max_length=150)

    def validate(self, data):
        return data

class UserPickSubmissionSerializer(serializers.Serializer):
    team = serializers.CharField(required=True, max_length=5)

    def validate(self, data):
        user = self.context.get('user')
        game_id = self.context.get('game_id')
        if user and UserPick.objects.filter(pickem__game_id=game_id, user=user).exists():
            raise serializers.ValidationError("User has already submitted a pick for this game.")
        team = Team.objects.filter(abbreviation=data['team']).first()
        game_pickem = GamePickem.objects.filter(game_id=game_id).first()
        if not team:
            raise serializers.ValidationError(f"Team with abbreviation {data.get('team')} does not exist.")
        if not game_pickem:
            raise serializers.ValidationError(f"Game with id {game_id} does not exist.")
        if game_pickem.status != PickemStatus.OPEN:
            raise serializers.ValidationError("Picks are closed for this game.")
        if team not in [game_pickem.game.home_team, game_pickem.game.away_team]:
            raise serializers.ValidationError("Selected team is not playing in this game.")
        return data

class LeaderboardQuerySerializer(serializers.Serializer):
    season = serializers.IntegerField(required=False, min_value=MIN_SEASON_YEAR, max_value=MAX_SEASON_YEAR)

    def validate(self, data):
        return data