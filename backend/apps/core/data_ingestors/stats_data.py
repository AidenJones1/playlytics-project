from apps.core.data_ingestors.counters import UpsertCounter
from apps.scheduling.models import Game
from apps.stats.models import TeamGameStats
from apps.teams.models import Team

def populate_stats_data(command, pbp_df):
    counter = UpsertCounter()

    # Group the play-by-play DataFrame and aggregate the relevant statistics
    game_stats_df = pbp_df.groupby(['season', 'game_id', 'posteam']).agg({
        "rush_attempt": "sum",
        "rushing_yards": lambda x: x[pbp_df["rush_attempt"] == 1].sum(),
        "rush_touchdown": lambda x: x[pbp_df["rush_touchdown"] == 1].sum(),
        "pass_attempt": "sum",
        "complete_pass": "sum",
        "passing_yards": lambda x: x[pbp_df["pass_attempt"] == 1].sum(),
        "pass_touchdown": lambda x: x[pbp_df["pass_touchdown"] == 1].sum(),
        "epa": lambda x: x[(pbp_df["pass_attempt"] == 1) | (pbp_df["rush_attempt"] == 1)].sum(),
        "success": lambda x: x[(pbp_df["pass_attempt"] == 1) | (pbp_df["rush_attempt"] == 1)].sum(),
        "interception": "sum",
        "fumble_lost": "sum",
        "sack": "sum", 
    })

    # Iterate through each game and team in the aggregated DataFrame
    for _, game_entry in game_stats_df.iterrows():
        game_id = game_entry.name[1]
        team_abbr = game_entry.name[2]

        # Retrieve the corresponding Game and Team objects
        game_obj = Game.objects.get(id=game_id)
        team_obj = Team.objects.get(abbreviation=team_abbr)
        if not game_obj or not team_obj:
            command.stdout.write(command.style.WARNING(f"Game or Team not found for game_id: {game_id}, team_abbr: {team_abbr}. Skipping."))
            continue

        # Create or update the TeamGameStats entry
        _, was_created = TeamGameStats.objects.update_or_create(
            game=game_obj,
            team=team_obj,
            defaults={
                "rushing_attempts": game_entry["rush_attempt"],
                "rushing_yards": game_entry["rushing_yards"],
                "passing_attempts": game_entry["pass_attempt"] - game_entry["sack"],
                "completed_passes": game_entry["complete_pass"],
                "passing_yards": game_entry["passing_yards"],
                "rushing_touchdowns": game_entry["rush_touchdown"],
                "passing_touchdowns": game_entry["pass_touchdown"],
                "total_epa_gained": float(game_entry["epa"]),
                "successful_plays": game_entry["success"],
                "interceptions_thrown": game_entry["interception"],
                "fumbles_lost": game_entry["fumble_lost"],
                "sacks_allowed": game_entry["sack"]
            }
        )

        # Update the counter based on whether the stats entry was created or updated
        counter.record(was_created)

    command.stdout.write(command.style.SUCCESS(f"Stats data ingestion complete. {counter.summary('team game stats')}"))