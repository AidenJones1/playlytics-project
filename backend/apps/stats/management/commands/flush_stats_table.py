from django.core.management.base import BaseCommand

from apps.stats.models import TeamGameStats

class Command(BaseCommand):
    help = "Flush all team game stats data from the database."

    def handle(self, *args, **options):
        # Prompt the user for confirmation
        response = input("Are you sure you want to flush all team game stats data from the database? This action cannot be undone. Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            self.stdout.write(self.style.WARNING("Operation cancelled. No team game stats data has been flushed."))
            return
        
        # Flush all team game stats data from the database
        TeamGameStats.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("All team game stats data has been flushed from the database."))