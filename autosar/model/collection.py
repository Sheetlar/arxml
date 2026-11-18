from typing import Iterable

from autosar.model.base import LangStr
from autosar.model.element import Element
from autosar.model.enums import AutoCollectEnum
from autosar.model.instance_ref import AnyInstanceRef
from autosar.model.languages_enum import LEnum


class Collection(Element):
    def __init__(
            self,
            auto_collect: AutoCollectEnum | None = None,
            collection_semantics: str | None = None,
            element_role: str | None = None,
            element_refs: Iterable[str] | None = None,
            source_element_refs: Iterable[str] | None = None,
            collected_instance: AnyInstanceRef | None = None,
            source_instances: Iterable[AnyInstanceRef] | None = None,
            *args, **kwargs,
    ):
        if kwargs.pop('long_name', None) is None and (n := kwargs.get('name')) is not None:
            ln = LangStr(n)
            ln.language = LEnum.ALL_LANGUAGES
            kwargs['long_name'] = ln
        super().__init__(*args, **kwargs)
        self.auto_collect = auto_collect
        self.collection_semantics = collection_semantics
        self.element_role = element_role
        self.element_refs = self.eval_children(element_refs)
        self.source_element_refs = self.eval_children(source_element_refs)
        self.collected_instance = collected_instance
        self.source_instances = self.eval_children(source_instances)
