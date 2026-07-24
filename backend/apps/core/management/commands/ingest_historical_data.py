from contextlib import redirect_stderr, redirect_stdout
from typing import Any
import nfl_data_py as nfl
import os

from django.core.management.base import BaseCommand, CommandParser

from apps.core import constants
from apps.core.data_ingestors import (
    scheduling_data,
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

        # Populate data
        scheduling_data.populate_season_data(self, schedule_df)
        scheduling_data.populate_week_data(self, schedule_df)
        scheduling_data.populate_game_data(self, schedule_df)