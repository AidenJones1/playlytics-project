from apps.core.constants import INACTIVE_TEAMS
from apps.core.data_ingestors.counters import UpsertCounter
from apps.teams.models import Team

def populate_team_data(command, team_df):
    counter = UpsertCounter()

    # Filter out inactive teams from the DataFrame
    team_df = team_df[~team_df["team_abbr"].isin(INACTIVE_TEAMS)].reset_index(drop=True)

    # Iterate through each team in the DataFrame
    for _, team_entry in team_df.iterrows():
        _, was_created = Team.objects.update_or_create(
            abbreviation=team_entry["team_abbr"],
            defaults={
                "fullname":team_entry['team_name'],
                'nickname': team_entry['team_nick'],
                'conference': team_entry['team_conf'],
                'division': team_entry['team_division'],
                'logo': "team_logos/" + team_entry['team_nick'].lower() + ".png",
                'color_1': team_entry['team_color'],
                'color_2': team_entry['team_color2'],
                'color_3': team_entry.get('team_color3', None),
                'color_4': team_entry.get('team_color4', None),
            }
        )

        # Update the counter based on whether the team was created or updated
        counter.record(was_created)

    command.stdout.write(command.style.SUCCESS(f"Team data ingestion complete. {counter.summary('team')}"))