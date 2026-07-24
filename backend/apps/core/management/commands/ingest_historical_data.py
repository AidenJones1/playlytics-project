from contextlib import redirect_stderr, redirect_stdout
import nfl_data_py as nfl
import os

from django.core.management.base import BaseCommand, CommandParser

from apps.core import constants
from apps.core.data_ingestors import (
    elo_ratings_data,
    injury_data,
    pickems_data,
    scheduling_data,
    standings_data,
    stats_data,
)

class Command(BaseCommand):
    help = "Ingest historical data into the database."

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--start_year",
            type=int,
            default=constants.HISTORICAL_START_YEAR,
            help=f"Start year for historical data ingestion (default: {constants.HISTORICAL_START_YEAR})"
        )
        parser.add_argument(
            "--end_year",
            type=int,
            default=constants.HISTORICAL_END_YEAR,
            help=f"End year for historical data ingestion (default: {constants.HISTORICAL_END_YEAR})"
        )

    def handle(self, *args, **options):
        start_year = options["start_year"]
        end_year = options["end_year"]
        years = list(range(start_year, end_year + 1))

        # Retrieve data from API
        schedule_df = nfl.import_schedules(years=years)
        injury_df = nfl.import_injuries(years=years)
        with open(os.devnull, "w") as null_out:
            with redirect_stdout(null_out), redirect_stderr(null_out):
                pbp_df = nfl.import_pbp_data(years=years)

        # Populate data
        scheduling_data.populate_season_data(self, schedule_df)
        scheduling_data.populate_week_data(self, schedule_df)
        scheduling_data.populate_game_data(self, schedule_df)

        standings_data.populate_standings_data(self, schedule_df)
        pickems_data.populate_pickems_data(self, schedule_df)
        elo_ratings_data.populate_ratings_data(self, schedule_df)
        
        stats_data.populate_stats_data(self, pbp_df)

        injury_data.populate_injury_data(self, injury_df)