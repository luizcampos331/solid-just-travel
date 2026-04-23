# after/app/application/packages/cancel_all_of_traveler.py — LSP cure
@dataclass(slots=True)
class CancelResult:
    cancelled: list[TravelPackage]
    skipped: list[TravelPackage]


class CancelAllOfTraveler:
    def __init__(self, repo, policy):
        self._reader = repo
        self._writer = repo
        self._policy = policy

    def execute(self, traveler_id: int) -> CancelResult:
        packages = self._reader.by_traveler(traveler_id)
        cancelled, skipped = [], []
        for package in packages:
            if package.refundable:                       # ← filtra ANTES
                updated = self._policy.cancel(package)
                self._writer.update(updated)
                cancelled.append(updated)
            else:
                skipped.append(package)                  # ← relata honesto
        return CancelResult(cancelled=cancelled, skipped=skipped)


# Sem bomba. Sem 500. Caller recebe AMBAS as listas.
