import uuid
import string
import secrets

from django.db import models, IntegrityError

from apps.pickems.choices import PickemStatus, GroupRole

class GamePickem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey('scheduling.Game', on_delete=models.CASCADE, related_name='pickems')
    status = models.CharField(max_length=10, choices=PickemStatus.choices, default=PickemStatus.CLOSED)
    opens_at = models.DateTimeField(blank=False, null=False)
    closes_at = models.DateTimeField(blank=False, null=False)

    class Meta:
        verbose_name = "Game Pickem"
        verbose_name_plural = "Game Pickems"
        db_table = "game_pickems"
        ordering = ['-game__week__season__year', '-game__week__week', 'game__game_time']

    def __str__(self):
        return f"Pickem for {self.game}"
    

class UserPick(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pickem = models.ForeignKey("pickems.GamePickem", on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('pickem', 'user')
        verbose_name = "User Pick"
        verbose_name_plural = "User Picks"
        db_table = "user_picks"

    def __str__(self):
        return f"{self.user} picked {self.team} for {self.pickem.game}"


class PickemGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    group_key = models.CharField(max_length=9, unique=True, db_index=True)
    is_private = models.BooleanField(default=True)
    invite_code = models.CharField(max_length=12, db_index=True)
    max_members = models.PositiveIntegerField(default=10)

    class Meta:
        verbose_name = "Pickem Group"
        verbose_name_plural = "Pickem Groups"
        db_table = "pickem_groups"

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self._generate_invite_code()

        if self.group_key:
            return super().save(*args, **kwargs)

        for _ in range(5):
            self.group_key = self._generate_group_key()
            try:
                return super().save(*args, **kwargs)
            except IntegrityError:
                self.group_key = None

        raise IntegrityError("Failed to generate a unique group key after multiple attempts.")

    @staticmethod
    def _generate_invite_code(length=12):
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def _generate_group_key(length=9):
        characters = string.ascii_uppercase + string.digits
        characters = characters.replace('0', '').replace('O', '').replace('I', '').replace('1', '').replace('L', '')
        return ''.join(secrets.choice(characters) for _ in range(length))

    def __str__(self):
        return f"{self.name}"


class PickemGroupMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey("pickems.PickemGroup", on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="pickem_memberships")
    role = models.CharField(max_length=10, choices=GroupRole.choices, default=GroupRole.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')
        verbose_name = "Pickem Group Member"
        verbose_name_plural = "Pickem Group Members"
        db_table = "pickem_group_members"

    def __str__(self):
        return f"{self.user} in {self.group} as {self.role}"