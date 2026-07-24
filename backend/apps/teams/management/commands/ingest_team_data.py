from django.core.management.base import BaseCommand

from apps.core.data_ingestors.team_data import populate_team_data

from nfl_data_py import import_team_desc

class Command(BaseCommand):
    help = "Ingest team data from the api and populate the database."

    def handle(self, *args, **options):
        team_df = import_team_desc()
        populate_team_data(self, team_df)