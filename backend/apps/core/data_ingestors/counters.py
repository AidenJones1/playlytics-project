from dataclasses import dataclass

@dataclass
class UpsertCounter:
    created: int = 0
    updated: int = 0

    def record(self, was_created: bool) -> None:
        if was_created:
            self.created += 1
        else:
            self.updated += 1

    def summary(self, object_label: str) -> str:
        return (
            f"{self.created} {object_label} object(s) created, "
            f"{self.updated} {object_label} object(s) updated."
        )


@dataclass
class WinLossTieCounter:
    wins: int = 0
    losses: int = 0
    ties: int = 0
    conference_wins: int = 0
    conference_losses: int = 0
    conference_ties: int = 0
    division_wins: int = 0
    division_losses: int = 0
    division_ties: int = 0
    home_wins: int = 0
    home_losses: int = 0
    home_ties: int = 0
    away_wins: int = 0
    away_losses: int = 0
    away_ties: int = 0
    streak_outcome: str = "-"
    streak_count: int = 0

    def record(self, result: int, is_home: bool, is_conference_game: bool, is_divisional_game: bool) -> None:
        # Normalize result to the selected team's perspective.
        perspective_result = result if is_home else -result

        if perspective_result > 0:
            outcome = 'wins'
        elif perspective_result < 0:
            outcome = 'losses'
        else:
            outcome = 'ties'

        setattr(self, outcome, getattr(self, outcome) + 1)

        location_outcome = f'home_{outcome}' if is_home else f'away_{outcome}'
        setattr(self, location_outcome, getattr(self, location_outcome) + 1)

        if is_conference_game:
            conference_outcome = f'conference_{outcome}'
            setattr(self, conference_outcome, getattr(self, conference_outcome) + 1)

        if is_divisional_game:
            division_outcome = f'division_{outcome}'
            setattr(self, division_outcome, getattr(self, division_outcome) + 1)

        if outcome == self.streak_outcome:
            self.streak_count += 1
        else:
            self.streak_outcome = outcome
            self.streak_count = 1

    @property
    def streak_label(self) -> str:
        if self.streak_count == 0:
            return '-'
        prefix_by_outcome = {
            'wins': 'W',
            'losses': 'L',
            'ties': 'T',
        }
        return f"{prefix_by_outcome[self.streak_outcome]}{self.streak_count}"

    def summary(self) -> str:
        return f"{self.wins} win(s), {self.losses} loss(es), {self.ties} tie(s)"


@ dataclass
class PointsCounter:
    points_for: int = 0
    points_against: int = 0

    def record(self, points_for: int, points_against: int) -> None:
        self.points_for += points_for
        self.points_against += points_against

    def summary(self) -> str:
        return f"{self.points_for} point(s) for, {self.points_against} point(s) against"