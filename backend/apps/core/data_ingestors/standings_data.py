from apps.core.data_ingestors.counters import UpsertCounter, WinLossTieCounter, PointsCounter
from apps.scheduling.models import Week
from apps.standings.models import TeamStandings
from apps.teams.models import Team

import pandas as pd

def populate_standings_data(command, schedule_df):
    counter = UpsertCounter()

    # Cache team objects by name so opponent conference/division lookups are cheap.
    teams_by_name = {team.abbreviation: team for team in Team.objects.all()}
    teams = schedule_df["home_team"].unique()
    schedule_df = schedule_df[schedule_df["game_type"] == "REG"]

    for year in schedule_df['season'].unique():
        season_schedule_df = schedule_df[schedule_df['season'] == year]

        schedules = pd.DataFrame()

        # Find the last regular season week for the given year
        weeks_for_season_objs = Week.objects.filter(season__year=year).order_by('-week')
        last_week = max(season_schedule_df['week'].unique())

        # Iterate through each week of the regular season to calculate standings
        for week in range(1, last_week + 1):
            week_obj = weeks_for_season_objs.filter(season__year=year, week=week).first()

            week_schedule_df = season_schedule_df[season_schedule_df['week'] == week]
            schedules = pd.concat([schedules, week_schedule_df], ignore_index=True)

            # Calculate standings for each team based on the schedule data
            for team in teams:
                team_schedule_df = schedules[
                    (schedules['home_team'] == team) | (schedules['away_team'] == team)
                ]
                team_obj = teams_by_name.get(team)

                if team_schedule_df.empty:
                    continue
                if team_obj is None:
                    continue

                # If it's the first week and there are no results, create a default standings entry
                if week == 1 and team_schedule_df['result'].dropna().empty:
                    _, was_created = TeamStandings.objects.update_or_create(
                        team=team_obj,
                        week=week_obj,
                        defaults={
                            "wins": 0,
                            "losses": 0,
                            "ties": 0,
                            "percentage": 0.0,
                            "home_wins": 0,
                            "home_losses": 0,
                            "home_ties": 0,
                            "away_wins": 0,
                            "away_losses": 0,
                            "away_ties": 0,
                            "conference_wins": 0,
                            "conference_losses": 0,
                            "conference_ties": 0,
                            "division_wins": 0,
                            "division_losses": 0,
                            "division_ties": 0,
                            "point_differential": 0,
                            "streak": "-",
                        }
                    )
                    counter.record(was_created)
                
                win_counter = WinLossTieCounter()
                points_counter = PointsCounter()

                # Iterate through each game in the team's schedule to calculate standings
                for _, row in team_schedule_df.iterrows():
                    if pd.isna(row["result"]):
                        continue

                    is_home_team = row["home_team"] == team
                    opponent_name = row["away_team"] if is_home_team else row["home_team"]
                    opponent_obj = teams_by_name.get(opponent_name)

                    # Determine if the game is a conference and/or division game
                    in_conference_game = (
                        opponent_obj is not None and opponent_obj.conference == team_obj.conference
                    )
                    in_division_game = (
                        opponent_obj is not None and opponent_obj.division == team_obj.division
                    )

                    win_counter.record(
                        result=row["result"],
                        is_home=is_home_team,
                        is_conference_game=in_conference_game,
                        is_divisional_game=in_division_game,
                    )
                    if is_home_team:
                        points_counter.record(
                            points_for=row["home_score"],
                            points_against=row["away_score"]
                        )
                    else:
                        points_counter.record(
                            points_for=row["away_score"],
                            points_against=row["home_score"]
                        )

                # Create standings object
                _, was_created = TeamStandings.objects.update_or_create(
                    team=team_obj,
                    week=week_obj,
                    defaults={
                        "wins": win_counter.wins,
                        "losses": win_counter.losses,
                        "ties": win_counter.ties,
                        "home_wins": win_counter.home_wins,
                        "home_losses": win_counter.home_losses,
                        "home_ties": win_counter.home_ties,
                        "away_wins": win_counter.away_wins,
                        "away_losses": win_counter.away_losses,
                        "away_ties": win_counter.away_ties,
                        "conference_wins": win_counter.conference_wins,
                        "conference_losses": win_counter.conference_losses,
                        "conference_ties": win_counter.conference_ties,
                        "division_wins": win_counter.division_wins,
                        "division_losses": win_counter.division_losses,
                        "division_ties": win_counter.division_ties,
                        "streak": win_counter.streak_label,
                        "points_for": points_counter.points_for,
                        "points_against": points_counter.points_against,
                    }
                )

                counter.record(was_created)

    command.stdout.write(command.style.SUCCESS(f"Standings data ingestion complete. {counter.summary('standings')}"))