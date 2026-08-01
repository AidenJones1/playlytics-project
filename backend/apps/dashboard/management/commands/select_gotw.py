from django.core.management.base import BaseCommand, CommandParser

from apps.core.utils.dates import get_current_season_year, get_current_week_number
from apps.core.utils.gotw_selection import (
    competitiveness,
    team_quality,
    stakes,
    narrative
)
from apps.dashboard.models import GameOfTheWeek
from apps.scheduling.models import Game

class Command(BaseCommand):
    help = "Select the Game of the Week."

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--season",
            type=int,
            default=get_current_season_year(),
            help="The season year for which to select the Game of the Week.",
        )
        parser.add_argument(
            "--week",
            type=int,
            default=get_current_week_number(),
            help="The week number for which to select the Game of the Week.",
        )

    def handle(self, *args, **options):
        season = options["season"]
        week = options["week"]

        if week == -1:
            weeks = list(range(1, 23))
        else:
            weeks = [week]

        for week in weeks:
            games_during_week = Game.objects.filter(week__season__year=season, week__week=week)
            game_ratings = {}
            for game in games_during_week:
                rating = (
                    competitiveness(game)
                    + team_quality(game)
                    + stakes(game)
                    #+ narrative(game)
                )
                game_ratings[game] = rating

            if not game_ratings:
                self.stdout.write(self.style.WARNING(f"No games found for season {season}, week {week}."))
                return
            selected_game = max(game_ratings, key=game_ratings.get)
            _, created = GameOfTheWeek.objects.update_or_create(
                week=selected_game.week,
                defaults={"game": selected_game},
            )