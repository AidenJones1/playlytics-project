from apps.core.data_ingestors.counters import UpsertCounter
from apps.scheduling.models import Week
from apps.teams.models import Team, TeamInjuryReport

def populate_injury_data(command, injury_df):
    counter = UpsertCounter()

    injury_df = injury_df.dropna(subset=['position', 'full_name', 'gsis_id', 'report_status'])

    # Iterate through each row in the injury DataFrame and update or create TeamInjuryReport entries
    for _, entry in injury_df.iterrows():
        position = entry['position']
        player_name = entry['full_name']
        player_id = entry['gsis_id']
        status = entry['report_status']
        team_abbreviation = entry['team']
        week = entry['week']
        season = entry['season']

        week_obj = Week.objects.get(season__year=season, week=week)
        team_obj = Team.objects.get(abbreviation=team_abbreviation)

        # Update or create the TeamInjuryReport entry in the database
        _, was_created = TeamInjuryReport.objects.update_or_create(
            player_id=player_id,
            team=team_obj,
            week=week_obj,
            defaults={
                'position': position,
                'player_name': player_name,
                'injury_status': status
            }
        )

        # Increment the counter based on whether the record was created or updated
        counter.record(was_created)

    command.stdout.write(command.style.SUCCESS(f"Injury data ingestion complete. {counter.summary('injury report')}"))