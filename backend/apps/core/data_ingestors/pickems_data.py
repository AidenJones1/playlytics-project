from datetime import datetime, time

from django.utils import timezone

from apps.core.data_ingestors.counters import UpsertCounter
from apps.pickems.choices import PickemStatus
from apps.pickems.models import GamePickem
from apps.scheduling.models import Game

def populate_pickems_data(command, schedule_df):
    counter = UpsertCounter()

    for _, game_entry in schedule_df.iterrows():
        game_id = game_entry['game_id']

        game_obj = Game.objects.get(id=game_id)
        if game_obj is None:
            command.stdout.write(command.style.WARNING(f"Game with ID {game_id} not found. Skipping."))
            continue

        # Find the timezone-aware open and close times for the pickem
        current_tz = timezone.get_default_timezone()
        opens_at = timezone.make_aware(
            datetime.combine(game_obj.week.start_date, time.min),
            current_tz,
        )
        closes_at = timezone.localtime(game_obj.game_time, current_tz)

        # Update or create the GamePickem entry for this game
        _, was_created = GamePickem.objects.update_or_create(
            game=game_obj,
            defaults={
                "opens_at": opens_at,  # Open picks at the start of the week
                "closes_at": closes_at,  # Close picks at game_time
                "status": PickemStatus.OPEN if timezone.now() < closes_at else PickemStatus.CLOSED,
            }
        )
        counter.record(was_created)

    command.stdout.write(command.style.SUCCESS(f"Game pickem data ingestion complete. {counter.summary('game pickem')}"))