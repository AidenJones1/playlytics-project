from django.core.management.base import BaseCommand

from apps.teams.models import Team, TeamInjuryReport

class Command(BaseCommand):
    help = "Flush all team data from the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-confirmation",
            action="store_true",
            help="Skip the confirmation prompt and flush the team data immediately. Use with caution, as this action cannot be undone."
        )
        parser.add_argument(
            "--team-data",
            action="store_true",
            help="Flush only the team data (Team model) from the database."
        )
        parser.add_argument(
            "--injury-data",
            action="store_true",
            help="Flush only the team injury report data (TeamInjuryReport model) from the database."
        )
        parser.add_argument(
            "--all-data",
            action="store_true",
            help="Flush both team data and team injury report data from the database."
        )

    def handle(self, *args, **options):
        response = 'yes'
        if not options["skip_confirmation"]:
            # Prompt the user for confirmation
            response = input("Are you sure you want to flush all specified team data from the database? This action cannot be undone. Type 'yes' to confirm: ")

        if response.lower() != 'yes':
            self.stdout.write(self.style.WARNING("Operation cancelled. No team data has been flushed."))
            return
        
        if options["all_data"]:
            Team.objects.all().delete()
            TeamInjuryReport.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("All team data (Team and TeamInjuryReport) has been flushed from the database."))
        else:
            if options["team_data"]:
                Team.objects.all().delete()
                self.stdout.write(self.style.SUCCESS("All team data (Team) has been flushed from the database."))
            if options["injury_data"]:
                TeamInjuryReport.objects.all().delete()
                self.stdout.write(self.style.SUCCESS("All team injury report data (TeamInjuryReport) has been flushed from the database."))