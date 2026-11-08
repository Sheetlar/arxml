from typing import Iterable

from autosar.model.ar_object import ArObject
from autosar.model.base import Identifiable
from autosar.model.element import Element


class Package(Identifiable):
    def __init__(
            self,
            packages: Iterable['Package'] | None = None,
            elements: Iterable[Element] | None = None,
            reference_bases: None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.packages = self._set_parent(packages)
        self.elements = self._set_parent(elements)
        self.reference_bases = reference_bases

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.packages
        yield from self.elements
