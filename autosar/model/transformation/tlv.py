from dataclasses import dataclass
from typing import Iterable

from autosar.model.ar_object import ArObject
from autosar.model.element import Element


@dataclass(repr=False)
class TlvDataIdDefinition(ArObject):
    id: int
    tlv_argument_ref: str | None = None
    tlv_implementation_data_type_element_ref: str | None = None
    tlv_record_element_ref: str | None = None


class TlvDataIdDefinitionSet(Element):
    def __init__(
            self,
            tlv_data_id_definitions: Iterable[TlvDataIdDefinition] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tlv_data_id_definitions = self.eval_children(tlv_data_id_definitions)
