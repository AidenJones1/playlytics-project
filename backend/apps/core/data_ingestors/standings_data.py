from apps.core.data_ingestors.counters import UpsertCounter
from apps.scheduling.models import Week
from apps.standings.models import TeamStandings
from apps.teams.models import Team

import pandas as pd

def populate_standings_data(command, schedule_df):
    counter = UpsertCounter()

    # Cache team objects by name so opponent conference/division lookups are cheap.
    teams_by_name = {team.abbreviation: team for team in Team.objects.all()}
    teams = schedule_df["home_team"].unique()

    for year in schedule_df['season'].unique():
        season_schedule_df = schedule_df[schedule_df['season'] == year]

        schedules = pd.DataFrame()

        # Find the last regular season week for the given year
        weeks_for_season_objs = Week.objects.filter(season__year=year).order_by('-week')
        last_week_obj = weeks_for_season_objs.first()
        if not last_week_obj:
            continue
        last_regular_season_week = last_week_obj.week

        # Iterate through each week of the regular season to calculate standings
        for week in range(1, last_regular_season_week + 1):
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
                
                wins = 0
                losses = 0
                ties = 0
                home_wins = 0
                home_losses = 0
                home_ties = 0
                away_wins = 0
                away_losses = 0
                away_ties = 0
                conference_wins = 0
                conference_losses = 0
                conference_ties = 0
                division_wins = 0
                division_losses = 0
                division_ties = 0
                point_differential = 0
                streak = 0

                # Iterate through each game in the team's schedule to calculate standings
                for _, row in team_schedule_df.iterrows():
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

                    # Get the result of the game
                    result = int(row["result"])
                    if is_home_team:
                        # If the evaluated team is the home team and won
                        if result > 0:
                            wins += 1
                            home_wins += 1
                            if in_conference_game:
                                conference_wins += 1
                            if in_division_game:
                                division_wins += 1
                            point_differential += abs(int(row["result"]))
                            streak = streak + 1 if streak >= 0 else 1

                        # If the evaluated team is the home team and lost
                        elif result < 0:
                            losses += 1
                            home_losses += 1
                            if in_conference_game:
                                conference_losses += 1
                            if in_division_game:
                                division_losses += 1
                            point_differential -= abs(int(row["result"]))
                            streak = streak - 1 if streak <= 0 else -1

                        # If the evaluated team is the home team and tied
                        else:
                            ties += 1
                            home_ties += 1
                            if in_conference_game:
                                conference_ties += 1
                            if in_division_game:
                                division_ties += 1
                            streak = 0
                            
                    else:
                        # If the evaluated team is the away team and won
                        if result < 0:
                            wins += 1
                            away_wins += 1
                            if in_conference_game:
                                conference_wins += 1
                            if in_division_game:
                                division_wins += 1
                            point_differential += abs(int(row["result"]))
                            streak = streak + 1 if streak >= 0 else 1

                        # If the evaluated team is the away team and lost
                        elif result > 0:
                            losses += 1
                            away_losses += 1
                            if in_conference_game:
                                conference_losses += 1
                            if in_division_game:
                                division_losses += 1
                            point_differential -= abs(int(row["result"]))
                            streak = streak - 1 if streak <= 0 else -1

                        # If the evaluated team is the away team and tied
                        else:
                            ties += 1
                            away_ties += 1
                            if in_conference_game:
                                conference_ties += 1
                            if in_division_game:
                                division_ties += 1
                            streak = 0
                
                # Calculate the number of games and winning percentage
                number_of_games = wins + losses + ties
                percentage = round(wins / number_of_games, 3) if number_of_games > 0 else 0.000

                # Format the streak for display
                if streak != 0:
                    streak = f"{'W' if streak > 0 else 'L'}{abs(streak)}"

                # Create standings object
                _, was_created = TeamStandings.objects.update_or_create(
                    team=team_obj,
                    week=week_obj,
                    defaults={
                        "wins": wins,
                        "losses": losses,
                        "ties": ties,
                        "percentage": percentage,
                        "home_wins": home_wins,
                        "home_losses": home_losses,
                        "home_ties": home_ties,
                        "away_wins": away_wins,
                        "away_losses": away_losses,
                        "away_ties": away_ties,
                        "conference_wins": conference_wins,
                        "conference_losses": conference_losses,
                        "conference_ties": conference_ties,
                        "division_wins": division_wins,
                        "division_losses": division_losses,
                        "division_ties": division_ties,
                        "point_differential": point_differential,
                        "streak": streak,
                    }
                )

                counter.record(was_created)

    command.stdout.write(command.style.SUCCESS(f"Standings data ingestion complete. {counter.summary('standings')}"))