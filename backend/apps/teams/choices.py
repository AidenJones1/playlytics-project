from django.db.models import TextChoices

class Conferences(TextChoices):
    AFC = 'AFC', 'AFC'
    NFC = 'NFC', 'NFC'

class Divisions(TextChoices):
    NFC_EAST = 'NFC East', 'NFC East'
    NFC_NORTH = 'NFC North', 'NFC North'
    NFC_SOUTH = 'NFC South', 'NFC South'
    NFC_WEST = 'NFC West', 'NFC West'
    AFC_EAST = 'AFC East', 'AFC East'
    AFC_NORTH = 'AFC North', 'AFC North'
    AFC_SOUTH = 'AFC South', 'AFC South'
    AFC_WEST = 'AFC West', 'AFC West'

CONFERENCE_DIVISION_CHOICES = [*Conferences.choices, *Divisions.choices]