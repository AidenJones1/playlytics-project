from django.db.models import QuerySet, Q

class GameQuerySet(QuerySet):
    def by_season_and_week(self, season, week):
        return self.filter(
            week__season__year=season,
            week__week=week
        )

    def by_division_teams(self, division):
        return self.filter(
            Q(home_team__division=division) | Q(away_team__division=division)
        )

    def by_conference_teams(self, conference):
        return self.filter(
            Q(home_team__conference=conference) | Q(away_team__conference=conference)
        )