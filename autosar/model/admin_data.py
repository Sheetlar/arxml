from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from autosar.model.ar_object import ArObject
from autosar.model.languages_enum import LEnum


class MultiLanguagePlainText(dict[str, str], ArObject):
    pass


@dataclass
class SpecialData(ArObject):
    gid: str
    value: str


@dataclass
class NumericalSpecialData(ArObject):
    gid: str
    value: int | float


@dataclass
class SpecialDataGroup(ArObject):  # SDGContents included
    gid: str
    contents: 'list[SpecialData | NumericalSpecialData | SpecialDataGroup | str] | None'
    caption: None = None

    def find(self, ref: str | None) -> 'SpecialData | NumericalSpecialData | SpecialDataGroup | None':
        if ref is None:
            return None
        if ref == '':
            return self
        if self.contents is None:
            return None
        top_gid, _, ref_tail = ref.partition('/')
        for item in self.contents:
            if isinstance(item, str):
                continue
            if item.gid == top_gid:
                if isinstance(item, SpecialDataGroup):
                    return item.find(ref_tail)
                return item
        return None


class AdminData(ArObject):
    def __init__(
            self,
            sdgs: Iterable[SpecialDataGroup] | None = None,
            language: LEnum | None = None,
            used_languages: MultiLanguagePlainText | None = None,
            doc_revision: None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.special_data_groups = self.eval_children(sdgs)
        self.language = language
        self.used_languages = used_languages
        self.doc_revision = doc_revision

    def find(self, ref: str | None) -> SpecialData | NumericalSpecialData | SpecialDataGroup | None:
        if ref is None:
            return None
        top_gid, _, ref_tail = ref.partition('/')
        for group in self.special_data_groups:
            if group.gid == top_gid:
                return group.find(ref_tail)
        return None
