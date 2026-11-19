from typing import Iterable, TypeVar

from autosar.model.ar_object import ArObject
from autosar.model.base import Identifiable
from autosar.model.element import Element
from autosar.model.enums import ByteOrderEnum


class PduToFrameMapping(Identifiable):
    def __init__(
            self,
            pdu_ref: str,
            packing_byte_order: ByteOrderEnum,
            start_position: int,
            update_indication_bit_position: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.pdu_ref = pdu_ref
        self.packing_byte_order = packing_byte_order
        self.start_position = start_position
        self.update_indication_bit_position = update_indication_bit_position


class Frame(Element):
    def __init__(
            self,
            frame_length: int,
            pdu_to_frame_mappings: Iterable[PduToFrameMapping] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.frame_length = frame_length
        self.pdu_to_frame_mappings = self._set_parent(pdu_to_frame_mappings)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.pdu_to_frame_mappings


AnyFrame = TypeVar('AnyFrame', bound=Frame)


class FrameTriggering(Identifiable):
    def __init__(
            self,
            frame_ref: str,
            frame_port_refs: Iterable[str] | None = None,
            pdu_triggering_refs: Iterable[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.frame_ref = frame_ref
        self.frame_port_refs = self.eval_children(frame_port_refs)
        self.pdu_triggering_refs = self.eval_children(pdu_triggering_refs)
