from django.core.management.base import BaseCommand

from apps.scheduling.models import Week, Season, Game

class Command(BaseCommand):
    help = "Flush all scheduling data from the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-confirmation",
            action="store_true",
            help="Skip the confirmation prompt and flush the scheduling data immediately. Use with caution, as this action cannot be undone."
        )
        parser.add_argument(
            "--seasons_table",
            action="store_true",
            help="Flush the seasons table. Flushing the seasons table also flushes all related weeks and games. Use with caution, as this action cannot be undone."
        )
        parser.add_argument(
            "--weeks_table",
            action="store_true",
            help="Flush the weeks table. Flushing the weeks table also flushes all related games. Use with caution, as this action cannot be undone."
        )
        parser.add_argument(
            "--games_table",
            action="store_true",
            help="Flush the games table. Use with caution, as this action cannot be undone."
        )
        parser.add_argument(
            "--all_tables",
            action="store_true",
            help="Flush all scheduling tables (seasons, weeks, and games). Use with caution, as this action cannot be undone."
        )

    def handle(self, *args, **options):
        all_tables = options["all_tables"]
        seasons_table = options["seasons_table"]
        weeks_table = options["weeks_table"]
        games_table = options["games_table"]

        response = 'yes'
        if not options["skip_confirmation"]:
            # Prompt the user for confirmation
            response = input("Are you sure you want to flush all the specified scheduling data from the database? This action cannot be undone. Type 'yes' to confirm: ")

        if response.lower() != 'yes':
            self.stdout.write(self.style.WARNING("Operation cancelled. No scheduling data has been flushed."))
            return

        # If no specific table is specified, flush all tables by default
        if not (seasons_table or weeks_table or games_table):
            all_tables = True 
        
        if all_tables:
            Week.objects.all().delete()
            Season.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("All scheduling data (seasons, weeks, and games) has been flushed from the database."))
        else:
            if weeks_table:
                Week.objects.all().delete()
                self.stdout.write(self.style.SUCCESS("All week data has been flushed from the database."))
            if games_table:
                Game.objects.all().delete()
                self.stdout.write(self.style.SUCCESS("All game data has been flushed from the database."))
            if seasons_table:
                Season.objects.all().delete()
                self.stdout.write(self.style.SUCCESS("All season data has been flushed from the database."))