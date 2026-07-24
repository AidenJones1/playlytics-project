from django.core.management.base import BaseCommand

from apps.standings.models import TeamStandings

class Command(BaseCommand):
    help = "Flush all standings data from the database."

    def handle(self, *args, **options):
        response = input("Are you sure you want to flush all standings data from the database? This action cannot be undone. Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            self.stdout.write(self.style.WARNING("Operation cancelled. No standings data has been flushed."))
            return
        
        TeamStandings.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("All standings data has been flushed from the database."))