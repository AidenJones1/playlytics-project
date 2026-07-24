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