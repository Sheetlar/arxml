from typing import Iterable, TypeVar

from autosar.model.element import Element


class PduToFrameMapping(Element):
    def __init__(
            self,
            packing_byte_order: str,
            pdu_ref: str,
            start_position: int,
            update_indication_bit_position: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.packing_byte_order = packing_byte_order
        self.pdu_ref = pdu_ref
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
        self._find_sets = (self.pdu_to_frame_mappings,)


class CanFrame(Frame):
    pass


class FlexrayFrame(Frame):
    pass


class GenericEthernetFrame(Frame):
    pass


class Ieee1722TpFrame(Frame):
    def __init__(
            self,
            relative_representation_time: float,
            stream_identifier: int,
            sub_type: int,
            version: int,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.relative_representation_time = relative_representation_time
        self.stream_identifier = stream_identifier
        self.sub_type = sub_type
        self.version = version


class UserDefinedEthernetFrame(Frame):
    pass


class LinEventTriggeredFrame(Frame):
    def __init__(
            self,
            collision_resolving_schedule_ref: str | None = None,
            lin_unconditional_frame_refs: list[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if lin_unconditional_frame_refs is None:
            lin_unconditional_frame_refs = []
        self.collision_resolving_schedule_ref = collision_resolving_schedule_ref
        self.lin_unconditional_frame_refs = lin_unconditional_frame_refs


class LinSporadicFrame(Frame):
    def __init__(
            self,
            substituted_frame_refs: list[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if substituted_frame_refs is None:
            substituted_frame_refs = []
        self.substituted_frame_refs = substituted_frame_refs


class LinUnconditionalFrame(Frame):
    pass


AnyFrame = TypeVar('AnyFrame', bound=Frame)
