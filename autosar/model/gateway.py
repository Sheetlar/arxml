from dataclasses import dataclass
from typing import Any, Iterable

from autosar.model.ar_object import ArObject
from autosar.model.element import Element


@dataclass
class DefaultValueElement(ArObject):
    element_byte_value: int
    element_position: int


@dataclass
class PduMappingDefaultValue(ArObject):
    default_value_elements: list[DefaultValueElement]


@dataclass
class TargetIPduRef(ArObject):
    target_i_pdu_ref: str
    default_value: PduMappingDefaultValue | None = None


@dataclass
class FrameMapping(ArObject):
    source_frame_ref: str
    target_frame_ref: str
    introduction: Any = None


@dataclass
class IPduMapping(ArObject):
    source_i_pdu_ref: str
    target_i_pdu: TargetIPduRef
    pdu_max_length: int | None = None
    pdu_r_tp_chunk_size: int | None = None
    introduction: Any = None


@dataclass
class ISignalMapping(ArObject):
    source_signal_ref: str
    target_signal_ref: str
    introduction: Any = None


class Gateway(Element):
    def __init__(
            self,
            ecu_ref: str | None = None,
            frame_mappings: Iterable[FrameMapping] | None = None,
            i_pdu_mappings: Iterable[IPduMapping] | None = None,
            signal_mappings: Iterable[ISignalMapping] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.ecu_ref = ecu_ref
        self.frame_mappings = self.eval_children(frame_mappings)
        self.i_pdu_mappings = self.eval_children(i_pdu_mappings)
        self.signal_mappings = self.eval_children(signal_mappings)
