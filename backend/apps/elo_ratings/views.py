from typing import cast

from django.utils.timezone import now
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from apps.core.serializers import SeasonWeekQuerySerializer
from apps.core.validators import validate_serializer
from apps.elo_ratings.models import TeamELORating
from apps.elo_ratings.querysets import TeamELORatingQuerySet
from apps.elo_ratings.serializers import TeamELORatingSerializer
from apps.scheduling.models import Week

class TeamELORatingsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        request = cast(Request, self.request)
        params = validate_serializer(SeasonWeekQuerySerializer, request.query_params)

        elo_qs = cast(TeamELORatingQuerySet, TeamELORating.objects)
        queryset = elo_qs.get_all_teams_recent_ratings(season=params['season'], week=params['week'])

        week_obj = Week.objects.get(season__year=params['season'], week=params['week'])
        if week_obj.end_date > now().date():
            return queryset.order_by(
                '-ratings_before',
                '-average_opponent_ratings',
                '-average_gain',
                '-highest_ratings',
                '-lowest_ratings',
                'team'
            )
        # If the week has ended, order by ratings after the week
        return queryset.order_by(
            '-ratings_after',
            '-average_opponent_ratings',
            '-average_gain',
            '-highest_ratings',
            '-lowest_ratings',
            'team'
        )

    # List all team ELO ratings for a given season and week, ordered by ratings before or after the week depending on whether the week has ended
    # GET /api/elo_ratings/ratings-standings/
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = TeamELORatingSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)