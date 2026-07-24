import uuid

from django.db import models

from apps.elo_ratings.querysets import TeamELORatingQuerySet

class TeamELORating(models.Model):
    objects = TeamELORatingQuerySet.as_manager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE)
    game = models.ForeignKey('scheduling.Game', on_delete=models.CASCADE)
    ratings_before = models.IntegerField(blank=False, null=False, default=1500)
    ratings_after = models.IntegerField(blank=True, null=True, default=1500)
    gained = models.IntegerField(blank=True, null=True, default=0)
    average_opponent_ratings = models.IntegerField(blank=False, null=False, default=1500)
    highest_ratings = models.IntegerField(blank=False, null=False, default=1500)
    lowest_ratings = models.IntegerField(blank=False, null=False, default=1500)
    average_gain = models.IntegerField(blank=False, null=False, default=0)

    class Meta:
        unique_together = ('team', 'game')
        verbose_name = "Team ELO Rating"
        verbose_name_plural = "Team ELO Ratings"
        db_table = "team_elo_ratings"
        ordering = ['-game__week__season__year', 'game__week__week', '-game__game_time', 'team__abbreviation']

    def __str__(self):
        return f"ELO rating for {self.team} - {self.game}"