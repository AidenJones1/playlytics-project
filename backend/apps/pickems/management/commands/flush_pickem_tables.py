from django.core.management.base import BaseCommand

from apps.pickems.models import (
    GamePickem,
    UserPick,
    PickemGroup,
    PickemGroupMember,
)

class Command(BaseCommand):
    help = "Flush all pickems data from the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-confirmation",
            action="store_true",
            help="Skip the confirmation prompt and flush the pickems data immediately. Use with caution, as this action cannot be undone."
        )
        parser.add_argument(
            "--game_pickem_table",
            action="store_true",
            help="Flush the game pickem table instead of the user pick table. Use with caution, as this action cannot be undone."
        )
        parser.add_argument(
            "--user_pick_table",
            action="store_true",
            help="Flush the user pick table instead of the game pickem table. Use with caution, as this action cannot be undone."
        )
        parser.add_argument(
            "--pickem_group_table",
            action="store_true",
            help="Flush the pickem group table instead of the pickem group member table. Use with caution, as this action cannot be undone."
        )
        parser.add_argument(
            "--pickem_group_member_table",
            action="store_true",
            help="Flush the pickem group member table instead of the pickem group table. Use with caution, as this action cannot be undone."
        )
        parser.add_argument(
            "--all_tables",
            action="store_true",
            help="Flush all pickems tables (game pickem, user pick, pickem group, and pickem group member). Use with caution, as this action cannot be undone."
        )

    def handle(self, *args, **options):
        response = 'yes'
        if not options["skip_confirmation"]:
            # Prompt the user for confirmation
            response = input("Are you sure you want to flush all specified pickems data from the database? This action cannot be undone. Type 'yes' to confirm: ")

        if response.lower() != 'yes':
            self.stdout.write(self.style.WARNING("Operation cancelled. No pickems data has been flushed."))
            return
        
        if options["all_tables"]:
            GamePickem.objects.all().delete()
            UserPick.objects.all().delete()
            PickemGroup.objects.all().delete()
            PickemGroupMember.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("All pickems data has been flushed from the database."))
        else:
            if options["game_pickem_table"]:
                GamePickem.objects.all().delete()
                self.stdout.write(self.style.SUCCESS("All game pickem data has been flushed from the database."))
            if options["user_pick_table"]:
                UserPick.objects.all().delete()
                self.stdout.write(self.style.SUCCESS("All user pick data has been flushed from the database."))
            if options["pickem_group_table"]:
                PickemGroup.objects.all().delete()
                self.stdout.write(self.style.SUCCESS("All pickem group data has been flushed from the database."))
            if options["pickem_group_member_table"]:
                PickemGroupMember.objects.all().delete()
                self.stdout.write(self.style.SUCCESS("All pickem group member data has been flushed from the database."))