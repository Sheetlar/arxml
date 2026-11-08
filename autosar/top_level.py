from typing import Iterable

from autosar.model.admin_data import AdminData
from autosar.model.ar_object import ArObject, MaybeArObject
from autosar.model.package import Package
from autosar.model.system import System


class Autosar(ArObject):
    def __init__(
            self,
            packages: Iterable[Package],
            admin_data: AdminData | None = None,
            file_info_comment: None = None,
            introduction: None = None,
            systems: Iterable[System] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.packages = self._set_parent(packages)
        self.admin_data = admin_data
        self.file_info_comment = file_info_comment
        self.introduction = introduction
        self.systems = self.eval_children(systems)

    @property
    def version(self) -> float:
        return 4.0

    @property
    def root(self) -> 'Autosar':
        return self

    @property
    def namespace(self) -> str:
        return ''

    @property
    def parent(self) -> 'Autosar':
        return self

    @property
    def ref(self) -> str:
        return ''

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.packages
        # TODO: Handling AUTOSAR_platform
        # yield AUTOSAR_PLATFORM_PACKAGE

    def find(self, ref: str | None) -> 'MaybeArObject':
        if ref is None:
            return None
        return super().find(ref.removeprefix('/'))
