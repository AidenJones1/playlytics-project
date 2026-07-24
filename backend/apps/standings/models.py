import uuid

from django.db import models

from apps.standings.querysets import TeamStandingsQuerySet

class TeamStandings(models.Model):
    objects = TeamStandingsQuerySet.as_manager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='standings')
    week = models.ForeignKey('scheduling.Week', on_delete=models.CASCADE, related_name='standings')
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    ties = models.PositiveIntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    home_wins = models.PositiveIntegerField(default=0)
    home_losses = models.PositiveIntegerField(default=0)
    home_ties = models.PositiveIntegerField(default=0)
    away_wins = models.PositiveIntegerField(default=0)
    away_losses = models.PositiveIntegerField(default=0)
    away_ties = models.PositiveIntegerField(default=0)
    conference_wins = models.PositiveIntegerField(default=0)
    conference_losses = models.PositiveIntegerField(default=0)
    conference_ties = models.PositiveIntegerField(default=0)
    division_wins = models.PositiveIntegerField(default=0)
    division_losses = models.PositiveIntegerField(default=0)
    division_ties = models.PositiveIntegerField(default=0)
    point_differential = models.IntegerField(default=0)
    streak = models.CharField(max_length=5, blank=False, null=False, default='-')

    class Meta:
        unique_together = ('team', 'week')
        verbose_name = 'Team Standings'
        verbose_name_plural = 'Team Standings'
        db_table = 'team_standings'
        ordering = ['-week__season__year', '-week__week', '-percentage', '-wins', 'losses', '-point_differential']

    def __str__(self):
        return f"{self.team.fullname} - Week {self.week.week}"