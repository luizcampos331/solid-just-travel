"""Email VO — minimal structural check.

Intentionally simple: we check for `@` only. A production system would use
a full validator, but the talk's point is that **validation belongs in the
domain, not in the ORM**. Upgrading this to a real email parser is a
one-line change with zero ripple effect — that's the SRP payoff.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if "@" not in (self.value or ""):
            raise ValueError("invalid email")

    def __str__(self) -> str:
        return self.value
