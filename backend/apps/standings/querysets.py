from django.db.models import QuerySet

class TeamStandingsQuerySet(QuerySet):
    def by_season_week(self, season, week):
        return self.filter(
            week__season__year=season,
            week__week=week
        )
    
    def by_division(self, division):
        return self.filter(
            team__division=division
        )
    
    def by_conference(self, conference):
        return self.filter(
            team__conference=conference
        )