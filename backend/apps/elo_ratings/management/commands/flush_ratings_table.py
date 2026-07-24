from django.core.management.base import BaseCommand

from apps.elo_ratings.models import TeamELORating

class Command(BaseCommand):
    help = "Flush all ELO ratings data from the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-confirmation",
            action="store_true",
            help="Skip the confirmation prompt and flush the ELO ratings data immediately. Use with caution, as this action cannot be undone."
        )

    def handle(self, *args, **options):
        response = 'yes'
        if not options["skip_confirmation"]:
            # Prompt the user for confirmation
            response = input("Are you sure you want to flush all ELO ratings data from the database? This action cannot be undone. Type 'yes' to confirm: ")

        if response.lower() != 'yes':
            self.stdout.write(self.style.WARNING("Operation cancelled. No ELO ratings data has been flushed."))
            return
        
        # Flush all ELO ratings data from the database
        TeamELORating.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("All ELO ratings data has been flushed from the database."))