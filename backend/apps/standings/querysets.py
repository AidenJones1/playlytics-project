from django.db.models import Case, ExpressionWrapper, F, FloatField, IntegerField, QuerySet, Value, When
from django.db.models.functions import Cast

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

    def apply_default_ordering(self):
        total_games = F('wins') + F('losses') + F('ties')
        weighted_wins = F('wins') + (F('ties') * Value(0.5))

        return self.annotate(
            ordering_percentage=Case(
                When(wins=0, losses=0, ties=0, then=Value(0.0)),
                default=ExpressionWrapper(
                    weighted_wins / Cast(total_games, FloatField()),
                    output_field=FloatField(),
                ),
                output_field=FloatField(),
            ),
            ordering_point_differential=ExpressionWrapper(
                Cast(F('points_for'), IntegerField()) - Cast(F('points_against'), IntegerField()),
                output_field=IntegerField(),
            ),
        ).order_by(
            '-ordering_percentage',
            '-wins',
            '-ordering_point_differential',
            'team'
        )
