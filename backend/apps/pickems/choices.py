from django.db.models import TextChoices

class PickemStatus(TextChoices):
    OPEN = "Open", "Open"
    CLOSED = "Closed", "Closed"

class GroupRole(TextChoices):
    OWNER = "Owner", "Owner"
    MEMBER = "Member", "Member"