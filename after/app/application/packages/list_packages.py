"""ListPackages use case — depends only on PackageReader."""

from after.app.domain.packages.package_repository import PackageReader
from after.app.domain.packages.travel_package import TravelPackage


class ListPackages:
    def __init__(self, reader: PackageReader):
        self._reader = reader

    def execute(self) -> list[TravelPackage]:
        return self._reader.list()
