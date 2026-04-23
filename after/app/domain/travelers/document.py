"""Document VO — CPF with 11 digits.

This is an SRP cure: the validation rule that lived inside the God Class
`Traveler.validate()` in `before/` is now a first-class domain concept. The
entity can assume its document is valid; validation happens at construction
of the VO.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Document:
    value: str

    def __post_init__(self) -> None:
        if not self.value or len(self.value) != 11 or not self.value.isdigit():
            raise ValueError("document must be an 11-digit CPF")

    def __str__(self) -> str:
        return self.value
