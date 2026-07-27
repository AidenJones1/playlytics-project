from django.db.models import QuerySet, OuterRef, Subquery

class TeamELORatingQuerySet(QuerySet):
    def get_all_teams_recent_ratings(self, season, week):
        latest_rating_id = self.filter(
            team=OuterRef('team'),
            game__week__season__year=season,
            game__week__week__lte=week,
        ).order_by(
            '-game__week__season__year',
            '-game__week__week',
            '-game__game_time',
            '-game__id',
        ).values('id')[:1]

        return self.filter(
            game__week__season__year=season,
            game__week__week__lte=week,
            id=Subquery(latest_rating_id),
        ).select_related('team', 'game', 'game__week', 'game__week__season')