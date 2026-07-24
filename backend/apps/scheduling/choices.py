from django.db.models import TextChoices

class SeasonType(TextChoices):
    REGULAR = "Regular", "Regular"
    PLAYOFFS = "Playoffs", "Playoffs"


class GameStatus(TextChoices):
    SCHEDULED = "Scheduled", "Scheduled"
    IN_PROGRESS = "In Progress", "In Progress"
    COMPLETED = "Completed", "Completed"
    CANCELED = "Canceled", "Canceled"
    POSTPONED = "Postponed", "Postponed"


class GameLocation(TextChoices):
    HOME = "Home", "Home"
    AWAY = "Away", "Away"
    NEUTRAL = "Neutral", "Neutral"