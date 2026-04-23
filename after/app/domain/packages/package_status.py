"""PackageStatus — enum of valid package states.

Replaces the loose string column (`"active" | "cancelled"`) in `before/`.
"""

from enum import Enum


class PackageStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
