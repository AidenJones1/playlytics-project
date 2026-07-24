from datetime import datetime, timedelta

from django.utils import timezone

from apps.core import constants
from apps.core.utils import math, dates, game
from apps.core.data_ingestors.counters import UpsertCounter
from apps.scheduling.models import Season, Week, Game
from apps.scheduling.choices import GameStatus
from apps.teams.models import Team

def populate_season_data(command, schedule_df):
    counter = UpsertCounter()

    # Iterate through each unique year in the schedule DataFrame
    for year in schedule_df['season'].unique():
        season_schedule_df = schedule_df[schedule_df['season'] == year]

        # Iterate through each season type (regular and playoffs) for the given year
        for season_type_group in [constants.REGULAR_SEASON_TYPES, constants.PLAYOFFS_SEASON_TYPES]:
            filtered_schedule_df = season_schedule_df[season_schedule_df['game_type'].isin(season_type_group)]
            if filtered_schedule_df.empty:
                command.stdout.write(command.style.WARNING(f"No data found for year {year} and season types {season_type_group}."))
                continue

            # Determine the start and end dates for the season based on the filtered schedule
            start_date = dates.to_date_object(filtered_schedule_df['gameday'].min())
            end_date = dates.to_date_object(filtered_schedule_df['gameday'].max())
            if start_date is None or end_date is None:
                command.stdout.write(command.style.WARNING(f"Skipping season {year} ({dates.get_season_type(season_type_group[0])}) because start/end dates are missing."))
                continue

            # Update or create the Season entry in the database
            _, was_created = Season.objects.update_or_create(
                year=year,
                season_type=dates.get_season_type(season_type_group[0]),
                defaults={
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )

            # Update the counter based on whether the season was created or updated
            counter.record(was_created)

    command.stdout.write(command.style.SUCCESS(f"Season data ingestion complete. {counter.summary('season')}"))


def populate_week_data(command, schedule_df):
    counter = UpsertCounter()

    # Iterate through each unique year in the schedule DataFrame
    for year in schedule_df['season'].unique():
        season_schedule_df = schedule_df[schedule_df['season'] == year]

        # Iterate through each unique week in the season's schedule
        for week in season_schedule_df['week'].unique():
            week_schedule_df = season_schedule_df[season_schedule_df['week'] == week]
            season_type = dates.get_season_type(week_schedule_df['game_type'].iloc[0])

            # Retrieve the corresponding Season object
            try:
                season_obj = Season.objects.get(
                    year=year,
                    season_type=season_type
                )
            except Season.DoesNotExist:
                command.stdout.write(command.style.WARNING(f"Season {year} ({season_type}) does not exist."))
                continue

            # Determine the start and end dates for the week based on the filtered schedule
            raw_start_date = dates.to_date_object(week_schedule_df['gameday'].min())
            days_back_to_tuesday = (raw_start_date.weekday() - 1) % 7 if raw_start_date else 0 # Start date should be the Tuesday of the week
            adjusted_start_date = raw_start_date - timedelta(days=days_back_to_tuesday) if raw_start_date else None
            end_date = dates.to_date_object(week_schedule_df['gameday'].max())

            # Update or create the Week entry in the database
            _, was_created = Week.objects.update_or_create(
                season=season_obj,
                week=week,
                defaults={
                    "start_date": adjusted_start_date,
                    "end_date": end_date,
                }
            )

            # Update the counter based on whether the week was created or updated
            counter.record(was_created)

    command.stdout.write(command.style.SUCCESS(f"Week data ingestion complete. {counter.summary('week')}"))


def populate_game_data(command, schedule_df):
    counter = UpsertCounter()

    # Iterate through each game entry in the schedule DataFrame
    for _, game_entry in schedule_df.iterrows():
        season = game_entry['season']
        season_type = dates.get_season_type(game_entry['game_type'])
        week = game_entry['week']
        
        # Convert the game date and time to a timezone-aware datetime object
        current_timezone = timezone.get_current_timezone()
        game_date = dates.to_date_object(game_entry['gameday'])
        game_time = dates.to_time_object(game_entry['gametime'])
        game_datetime = datetime.strptime(f"{game_date} {game_time}", "%Y-%m-%d %H:%M:%S")
        game_datetime = timezone.make_aware(game_datetime, current_timezone)

        # Retrieve the corresponding Week object
        try:
            week_obj = Week.objects.get(
                season__year=season,
                season__season_type=season_type,
                week=week
            )
        except Week.DoesNotExist:
            command.stdout.write(command.style.WARNING(f"Week {week} for Season {season} ({season_type}) does not exist."))
            continue

        # Retrive the corresponding home and away Team objects
        try:
            home_team_obj = Team.objects.get(abbreviation=game_entry['home_team'])
            away_team_obj = Team.objects.get(abbreviation=game_entry['away_team'])
        except Team.DoesNotExist:
            command.stdout.write(command.style.WARNING(f"One or both teams ({game_entry['home_team']}, {game_entry['away_team']}) do not exist."))
            continue

        # Retrieve game details
        game_id = game_entry['game_id']
        home_score = math.to_nullable_int(game_entry['home_score'])
        away_score = math.to_nullable_int(game_entry['away_score'])
        home_rest_days = math.to_nullable_int(game_entry['home_rest'])
        away_rest_days = math.to_nullable_int(game_entry['away_rest'])
        location = game.get_game_location(game_entry['location'])
        venue = game_entry['stadium']
        status = GameStatus.COMPLETED if home_score is not None and away_score is not None else GameStatus.SCHEDULED

        # Update or create the Game entry in the database
        _, was_created = Game.objects.update_or_create(
            id=game_id,
            defaults={
                "week": week_obj,
                "home_team": home_team_obj,
                "away_team": away_team_obj,
                "game_time": game_datetime,
                "home_score": home_score,
                "away_score": away_score,
                "home_rest_days": home_rest_days,
                "away_rest_days": away_rest_days,
                "status": status,
                "location": location,
                "venue": venue,
            }
        )

        # Update the counter based on whether the game was created or updated
        counter.record(was_created)

    command.stdout.write(command.style.SUCCESS(f"Game data ingestion complete. {counter.summary('game')}"))