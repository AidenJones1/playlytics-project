from django.db import models

from apps.teams.choices import Conferences, Divisions, InjuryStatus
from apps.teams.querysets import TeamQuerySet, TeamInjuryReportQuerySet

class Team(models.Model):
    objects = TeamQuerySet.as_manager()

    abbreviation = models.CharField(primary_key=True, max_length=5)
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)
    fullname = models.CharField(max_length=100, blank=False, null=False)
    nickname = models.CharField(max_length=50, blank=False, null=False)
    conference = models.CharField(choices=Conferences.choices, max_length=3, blank=False, null=False)
    division = models.CharField(choices=Divisions.choices, max_length=10, blank=False, null=False)
    color_1 = models.CharField(max_length=7, blank=False, null=False)  # Hex color code
    color_2 = models.CharField(max_length=7, blank=False, null=False) # Hex color code
    color_3 = models.CharField(max_length=7, blank=True, null=True) # Hex color code, optional
    color_4 = models.CharField(max_length=7, blank=True, null=True) # Hex color code, optional

    class Meta:
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        db_table = 'teams'
        ordering = ['abbreviation']

    def __str__(self):
        return f"{self.fullname}"


class TeamInjuryReport(models.Model):
    objects = TeamInjuryReportQuerySet.as_manager()

    week = models.ForeignKey('scheduling.Week', on_delete=models.CASCADE, related_name='team_injury_reports')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='injury_reports')
    injury_status = models.CharField(choices=InjuryStatus.choices, max_length=20, blank=False, null=False)
    position = models.CharField(max_length=5, blank=False, null=False)
    player_id = models.CharField(max_length=50, blank=False, null=False)
    player_name = models.CharField(max_length=100, blank=False, null=False)

    class Meta: 
        verbose_name = "Team Injury Report"
        verbose_name_plural = "Team Injury Reports"
        db_table = "team_injury_reports"
        ordering = ['week', 'team', 'player_name']

    def __str__(self):
        return f"{self.week} - {self.team} - {self.position} - {self.player_name}"