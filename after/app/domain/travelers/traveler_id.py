"""TravelerId — typed wrapper over int to avoid primitive obsession.

Using a NewType makes `def by_id(id: TravelerId)` and `def by_id(id: int)`
distinct to type checkers, which prevents accidentally passing, say, a
package id where a traveler id is expected.
"""

from typing import NewType

TravelerId = NewType("TravelerId", int)
