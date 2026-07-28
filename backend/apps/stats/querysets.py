from django.db.models import Case, Count, F, Q, QuerySet, Sum, When

from apps.scheduling.choices import SeasonType


class TeamGameStatsQuerySet(QuerySet):
    @staticmethod
    def _offense_aggregate_fields():
        return {
            'games_played': Count('id'),
            'total_rushing_attempts': Sum('rushing_attempts'),
            'total_rushing_yards': Sum('rushing_yards'),
            'total_passing_attempts': Sum('passing_attempts'),
            'total_completed_passes': Sum('completed_passes'),
            'total_passing_yards': Sum('passing_yards'),
            'total_rushing_touchdowns': Sum('rushing_touchdowns'),
            'total_passing_touchdowns': Sum('passing_touchdowns'),
            'total_touchdowns': Sum('rushing_touchdowns') + Sum('passing_touchdowns'),
            'total_sacks_allowed': Sum('sacks_allowed'),
            'total_interceptions_thrown': Sum('interceptions_thrown'),
            'total_fumbles_lost': Sum('fumbles_lost'),
            'total_turnovers_given': Sum('interceptions_thrown') + Sum('fumbles_lost'),
            'total_successful_plays': Sum('successful_plays'),
        }

    @staticmethod
    def _defense_aggregate_fields():
        return {
            'games_played': Count('id'),
            'rushes_defended': Sum('rushing_attempts'),
            'rushing_yards_allowed': Sum('rushing_yards'),
            'passes_defended': Sum('passing_attempts'),
            'completions_allowed': Sum('completed_passes'),
            'passing_yards_allowed': Sum('passing_yards'),
            'rushing_touchdowns_allowed': Sum('rushing_touchdowns'),
            'passing_touchdowns_allowed': Sum('passing_touchdowns'),
            'total_touchdowns_allowed': Sum('rushing_touchdowns') + Sum('passing_touchdowns'),
            'sacks_made': Sum('sacks_allowed'),
            'interceptions_made': Sum('interceptions_thrown'),
            'fumbles_taken': Sum('fumbles_lost'),
            'total_turnovers_taken': Sum('interceptions_thrown') + Sum('fumbles_lost'),
            'total_successful_plays_allowed': Sum('successful_plays'),
        }

    @staticmethod
    def _games_before_target(game):
        return (
            Q(game__week__week__lt=game.week.week)
            | Q(game__week__week=game.week.week, game__game_time__lt=game.game_time)
            | Q(game__week__week=game.week.week, game__game_time=game.game_time, game_id__lt=game.id)
        )

    def _prior_team_game_ids(self, team, game, window):
        return list(
            self.filter(team=team, game__week__season__year=game.week.season.year)
            .filter(self._games_before_target(game))
            .order_by('-game__week__week', '-game__game_time', '-game_id')
            .values_list('game_id', flat=True)[:window]
        )

    def by_season(self, season, regular_season_only=True):
        queryset = self.filter(game__week__season__year=season)
        if regular_season_only:
            queryset = queryset.filter(game__week__season__season_type=SeasonType.REGULAR)
        return queryset

    def by_season_and_team(self, season, team, regular_season_only=True):
        return self.by_season(season, regular_season_only).filter(team=team)

    def agg_team_seasonal_offense_stats(self, game, team):
        return self.filter(
            game__week__season__year=game.week.season.year,
            game__week__week__lte=game.week.week,
            team=team,
        ).aggregate(**self._offense_aggregate_fields())

    def agg_team_seasonal_defense_stats(self, game, team):
        return self.filter(
            game__week__season__year=game.week.season.year,
            game__week__week__lte=game.week.week,
        ).filter(
            Q(game__home_team=team) | Q(game__away_team=team)
        ).exclude(team=team).aggregate(**self._defense_aggregate_fields())

    def agg_team_rolling_offense_stats(self, team, game, window):
        prior_game_ids = self._prior_team_game_ids(team, game, window)

        return self.filter(team=team, game_id__in=prior_game_ids).aggregate(**self._offense_aggregate_fields())

    def agg_team_rolling_defense_stats(self, team, game, window):
        prior_game_ids = self._prior_team_game_ids(team, game, window)

        return self.filter(game_id__in=prior_game_ids).exclude(team=team).aggregate(**self._defense_aggregate_fields())

    def agg_season_offense_stats(self):
        return (
            self.values('team__abbreviation')
            .annotate(**self._offense_aggregate_fields())
            .order_by('team__abbreviation')
        )

    def agg_season_defense_stats(self):
        return (
            self.annotate(
                defense_team_abbreviation=Case(
                    When(team=F('game__home_team'), then=F('game__away_team__abbreviation')),
                    default=F('game__home_team__abbreviation'),
                )
            )
            .values('defense_team_abbreviation')
            .annotate(**self._defense_aggregate_fields())
            .order_by('defense_team_abbreviation')
        )