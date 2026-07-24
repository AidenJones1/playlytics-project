from decimal import Decimal
import uuid

from django.db import models

from apps.stats.querysets import TeamGameStatsQuerySet

class TeamGameStats(models.Model):
    objects = TeamGameStatsQuerySet.as_manager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey('scheduling.Game', on_delete=models.CASCADE, related_name='team_game_stats')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='team_game_stats')
    rushing_attempts = models.IntegerField(blank=False, null=False, default=0)
    rushing_yards = models.IntegerField(blank=False, null=False, default=0)
    passing_attempts = models.IntegerField(blank=False, null=False, default=0)
    completed_passes = models.IntegerField(blank=False, null=False, default=0)
    passing_yards = models.IntegerField(blank=False, null=False, default=0)
    rushing_touchdowns = models.IntegerField(blank=False, null=False, default=0)
    passing_touchdowns = models.IntegerField(blank=False, null=False, default=0)
    sacks_allowed = models.IntegerField(blank=False, null=False, default=0)
    interceptions_thrown = models.IntegerField(blank=False, null=False, default=0)
    fumbles_lost = models.IntegerField(blank=False, null=False, default=0)
    total_epa_gained = models.DecimalField(blank=False, null=False, default=Decimal("0.0"), max_digits=15, decimal_places=12)
    successful_plays = models.IntegerField(blank=False, null=False, default=0)

    class Meta:
        unique_together = ('game', 'team')
        verbose_name = "Team Game Stat"
        verbose_name_plural = "Team Game Stats"
        db_table = "team_game_stats"
        ordering = ['-game__week__season__year', 'game__week__week', "game__game_time"]

    def __str__(self):
        return f"Team game stats for {self.team} - {self.game}"