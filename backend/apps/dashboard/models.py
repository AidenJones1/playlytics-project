import uuid

from django.db import models

class GameOfTheWeek(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    week = models.ForeignKey('scheduling.Week', on_delete=models.CASCADE, related_name='game_of_the_week')
    game = models.ForeignKey('scheduling.Game', on_delete=models.CASCADE, related_name='game_of_the_week')

    class Meta:
        unique_together = ('week', 'game')
        verbose_name = 'Game of the Week'
        verbose_name_plural = 'Games of the Week'
        db_table = "game_of_the_week"
        ordering = ['-week__season__year', '-week__week', 'game__game_time']

    def __str__(self):
        return f"Game of the Week: {self.game.home_team} vs {self.game.away_team} - Week {self.week.week}, {self.week.season.year}"