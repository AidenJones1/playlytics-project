import uuid

from django.db import models

from apps.scheduling.choices import SeasonType, GameStatus, GameLocation

class Season(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.PositiveIntegerField(blank=False, null=False)
    season_type = models.CharField(choices=SeasonType.choices, max_length=15, blank=False, null=False)
    start_date = models.DateField(blank=False, null=False)
    end_date = models.DateField(blank=False, null=False)

    class Meta:
        unique_together = ('year', 'season_type')
        verbose_name = 'Season'
        verbose_name_plural = 'Seasons'
        db_table = "seasons"
        ordering = ['-year', 'season_type']

    def __str__(self):
        if self.season_type == SeasonType.REGULAR:
            return f"{self.year} Regular Season"
        elif self.season_type == SeasonType.PLAYOFFS:
            return f"{self.year} Playoffs"


class Week(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    season = models.ForeignKey('scheduling.Season', on_delete=models.CASCADE, related_name='weeks')
    week = models.PositiveIntegerField(blank=False, null=False)
    start_date = models.DateField(blank=False, null=False)
    end_date = models.DateField(blank=False, null=False)

    class Meta:
        unique_together = ('season', 'week')
        verbose_name = 'Week'
        verbose_name_plural = 'Weeks'
        db_table = "weeks"
        ordering = ['-season__year', 'week']

    def __str__(self):
        return f"Week {self.week}, {self.season.year}"


class Game(models.Model):
    id = models.CharField(primary_key=True, max_length=255, editable=False)
    week = models.ForeignKey('scheduling.Week', on_delete=models.CASCADE, related_name='games', blank=False, null=False)
    game_time = models.DateTimeField(blank=False, null=False)
    home_team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='home_games')
    away_team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='away_games')
    home_score = models.PositiveIntegerField(blank=True, null=True)
    away_score = models.PositiveIntegerField(blank=True, null=True)
    home_rest_days = models.PositiveIntegerField(blank=True, null=True)
    away_rest_days = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(choices=GameStatus.choices, default=GameStatus.SCHEDULED, max_length=15, blank=False, null=False)
    location = models.CharField(choices=GameLocation.choices, default=GameLocation.NEUTRAL, max_length=15, blank=False, null=False)
    venue = models.CharField(max_length=255, blank=True, null=True)

    @property
    def result(self):
        if self.home_score is None or self.away_score is None:
            return None
        return self.home_score - self.away_score

    class Meta:
        unique_together = ("week", "home_team", "away_team")
        verbose_name = "Game"
        verbose_name_plural = "Games"
        db_table = "games"
        ordering = ['-week__season__year', 'week__week', 'game_time']
        
    def __str__(self):
        return f"{self.week}: {self.away_team} @ {self.home_team}"