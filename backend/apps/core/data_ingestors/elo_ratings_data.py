from collections import defaultdict
import pandas as pd

from apps.core import constants as constants
from apps.core.data_ingestors.counters import UpsertCounter
from apps.core.utils import elo_ratings
from apps.elo_ratings.models import TeamELORating
from apps.scheduling.models import Game
from apps.teams.models import Team

def populate_ratings_data(command, schedule_df):
    counter = UpsertCounter()

    # Cache all teams to avoid repeated database queries
    teams_by_abbreviation = {t.abbreviation: t for t in Team.objects.all()}

    for season in schedule_df['season'].unique():
        season_schedule_df = schedule_df[schedule_df['season'] == season]

        # Initialize ELO ratings for all teams at the start of the season
        current_elo_ratings = defaultdict(lambda: constants.INITIAL_ELO)
        team_history = defaultdict(list)

        for week in season_schedule_df['week'].unique():
            week_schedule_df = season_schedule_df[season_schedule_df['week'] == week]

            for _, game_entry in week_schedule_df.iterrows():
                home_team_abbr = game_entry['home_team']
                away_team_abbr = game_entry['away_team']
                game_id = game_entry['game_id']
                result = game_entry['result']

                # Retrieve the game object from the database
                game_object = Game.objects.filter(id=game_id).first()
                if game_object is None:
                    command.stdout.write(command.style.WARNING(f"Game with ID {game_id} not found. Skipping."))
                    continue

                # Get team objects from cache
                home_team_object = teams_by_abbreviation.get(home_team_abbr)
                away_team_object = teams_by_abbreviation.get(away_team_abbr)
                if home_team_object is None or away_team_object is None:
                    command.stdout.write(command.style.WARNING(f"One of the teams ({home_team_abbr}, {away_team_abbr}) not found. Skipping."))
                    continue

                if pd.isna(result):
                    # Create baseline ratings for unplayed Week 1 games.
                    if week == 1:
                        home_elo_before = current_elo_ratings[home_team_abbr]
                        away_elo_before = current_elo_ratings[away_team_abbr]

                        _, was_home_created = TeamELORating.objects.update_or_create(
                            team=home_team_object,
                            game=game_object,
                            defaults={
                                'ratings_before': home_elo_before,
                                'ratings_after': home_elo_before,
                                'gained': 0,
                                'average_opponent_ratings': away_elo_before,
                                'highest_ratings': home_elo_before,
                                'lowest_ratings': home_elo_before,
                                'average_gain': 0,
                            }
                        )
                        counter.record(was_home_created)
                        _, was_away_created = TeamELORating.objects.update_or_create(
                            team=away_team_object,
                            game=game_object,
                            defaults={
                                'ratings_before': away_elo_before,
                                'ratings_after': away_elo_before,
                                'gained': 0,
                                'average_opponent_ratings': home_elo_before,
                                'highest_ratings': away_elo_before,
                                'lowest_ratings': away_elo_before,
                                'average_gain': 0,
                            }
                        )
                        counter.record(was_away_created)

                location = game_entry['location']

                home_elo_before = current_elo_ratings[home_team_abbr]
                away_elo_before = current_elo_ratings[away_team_abbr]

                # Calculate the adjusted ELO ratings based on home field advantage
                adjusted_home_elo_ratings = home_elo_before + constants.HOME_FIELD_ADVANTAGE if location == "Home" else home_elo_before
                home_win_probability = elo_ratings.calculate_elo_win_probability(adjusted_home_elo_ratings, away_elo_before)
                margin_of_victory_bonus = elo_ratings.calculate_elo_mov_multiplier(result, home_elo_before, away_elo_before)

                # home win
                if result > 0:
                    delta = constants.K_FACTOR * margin_of_victory_bonus * (1 - home_win_probability)
                # home loss
                elif result < 0:
                    delta = constants.K_FACTOR * margin_of_victory_bonus * (0 - home_win_probability)
                # tie
                else:
                    delta = constants.K_FACTOR * margin_of_victory_bonus * (0.5 - home_win_probability)
                delta = round(delta)

                # Update ELO ratings for both teams
                home_elo_after = home_elo_before + delta
                away_elo_after = away_elo_before - delta

                current_elo_ratings[home_team_abbr] = home_elo_after
                current_elo_ratings[away_team_abbr] = away_elo_after

                # Append to history
                team_history[home_team_abbr].append({'elo_after': home_elo_after, 'gain': delta,  'opp_elo': away_elo_before})
                team_history[away_team_abbr].append({'elo_after': away_elo_after, 'gain': -delta, 'opp_elo': home_elo_before})

                # Derive statistics for both teams
                def _derive_stats(abbr):
                    history = team_history[abbr]
                    avg_opp_elo    = round(sum(h['opp_elo']  for h in history) / len(history))
                    highest_elo    = max(h['elo_after'] for h in history)
                    lowest_elo     = min(h['elo_after'] for h in history)
                    gains          = [h['gain'] for h in history]
                    avg_gain       = round(sum(gains) / len(gains))
                    return avg_opp_elo, highest_elo, lowest_elo, avg_gain
                home_avg_opp, home_high, home_low, home_avg_gain = _derive_stats(home_team_abbr)
                away_avg_opp, away_high, away_low, away_avg_gain = _derive_stats(away_team_abbr)

                # Create or update TeamELORating objects for both teams
                _, was_home_created = TeamELORating.objects.update_or_create(
                    team=home_team_object,
                    game=game_object,
                    defaults={
                        'ratings_before': home_elo_before,
                        'ratings_after': home_elo_after,
                        'gained': delta,
                        'average_opponent_ratings': home_avg_opp,
                        'highest_ratings': home_high,
                        'lowest_ratings': home_low,
                        'average_gain': home_avg_gain,
                    }
                )
                counter.record(was_home_created)
                _, was_away_created = TeamELORating.objects.update_or_create(
                    team=away_team_object,
                    game=game_object,
                    defaults={
                        'ratings_before': away_elo_before,
                        'ratings_after': away_elo_after,
                        'gained': -delta,
                        'average_opponent_ratings': away_avg_opp,
                        'highest_ratings': away_high,
                        'lowest_ratings': away_low,
                        'average_gain': away_avg_gain,
                    }
                )
                counter.record(was_away_created)
                
    command.stdout.write(command.style.SUCCESS(f"Successfully ingested ELO ratings data. {counter.summary('team ELO ratings')}"))