from django.core.management.base import BaseCommand

from apps.teams.models import Team

class Command(BaseCommand):
    help = "Flush all team data from the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-confirmation",
            action="store_true",
            help="Skip the confirmation prompt and flush the team data immediately. Use with caution, as this action cannot be undone."
        )

    def handle(self, *args, **options):
        response = 'yes'
        if not options["skip_confirmation"]:
            # Prompt the user for confirmation
            response = input("Are you sure you want to flush all specified team data from the database? This action cannot be undone. Type 'yes' to confirm: ")

        if response.lower() != 'yes':
            self.stdout.write(self.style.WARNING("Operation cancelled. No team data has been flushed."))
            return

        Team.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Successfully flushed all team data from the database."))

        
        
        