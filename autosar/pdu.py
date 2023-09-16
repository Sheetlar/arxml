from dataclasses import dataclass
from typing import Iterable

from autosar.ar_object import ArObject
from autosar.element import Element


@dataclass
class SecureCommunicationProps(ArObject):
    authentication_build_attempts: int | None = None
    authentication_retries: int | None = None
    data_id: int | None = None
    freshness_value_id: int | None = None
    message_link_length: int | None = None
    message_link_position: int | None = None


@dataclass
class ContainedIPduProps(ArObject):
    collection_semantics: str | None = None
    offset: int | None = None
    trigger: str | None = None

    def __post_init__(self):
        if self.offset is None:
            self.offset = 0


@dataclass
class SegmentPosition(ArObject):
    segment_byte_order: str | None = None
    segment_length: int | None = None
    segment_position: int | None = None

    def __post_init__(self):
        if self.segment_length is None:
            self.segment_length = 0
        if self.segment_position is None:
            self.segment_position = 0


@dataclass
class DynamicPartAlternative(ArObject):
    i_pdu_ref: str | None = None
    initial_dynamic_part: bool = False
    selector_field_code: int | None = None


class DynamicPart(ArObject):
    def __init__(
            self,
            segment_positions: list[SegmentPosition] | None = None,
            dynamic_part_alternatives: list[DynamicPartAlternative] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if segment_positions is None:
            segment_positions = []
        self.segment_position = segment_positions
        if dynamic_part_alternatives is None:
            dynamic_part_alternatives = []
        self.dynamic_part_alternatives = dynamic_part_alternatives


class StaticPart(ArObject):
    def __init__(
            self,
            segment_positions: list[SegmentPosition] | None = None,
            i_pdu_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if segment_positions is None:
            segment_positions = []
        self.segment_positions = segment_positions
        self.i_pdu_ref = i_pdu_ref


class IPduTiming(ArObject):
    ...


class ISignalToIPduMapping(Element):
    def __init__(
            self,
            i_signal_ref: str | None = None,
            packing_byte_order: str | None = None,
            start_position: int | None = None,
            transfer_property: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.i_signal_ref = i_signal_ref
        self.packing_byte_order = packing_byte_order
        if start_position is None:
            start_position = 0
        self.start_position = start_position
        self.transfer_property = transfer_property


class Pdu(Element):
    def __init__(
            self,
            length: int | None = None,
            unused_bit_pattern: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.length = length
        self.unused_bit_pattern = unused_bit_pattern


class NPdu(Pdu):
    pass


class NMPdu(Pdu):
    pass


class GeneralPurposePdu(Pdu):
    pass


class ISignalIPdu(Pdu):
    def __init__(
            self,
            contained_i_pdu_props: ContainedIPduProps | None = None,
            i_pdu_timing_specifications: list[IPduTiming] | None = None,
            i_signal_to_pdu_mappings: Iterable[ISignalToIPduMapping] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.contained_i_pdu_props = contained_i_pdu_props
        if i_pdu_timing_specifications is None:
            i_pdu_timing_specifications = []
        self.i_pdu_timing_specifications = i_pdu_timing_specifications
        self.i_signal_to_pdu_mappings = self._set_parent(i_signal_to_pdu_mappings)
        self._find_sets = [self.i_signal_to_pdu_mappings]


class ContainerIPdu(Pdu):
    def __init__(
            self,
            contained_pdu_triggering_refs: list[str] | None = None,
            container_trigger: str | None = None,
            header_type: str | None = None,
            rx_accept_contained_i_pdu: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if contained_pdu_triggering_refs is None:
            contained_pdu_triggering_refs = []
        self.contained_pdu_triggering_refs = contained_pdu_triggering_refs
        self.container_trigger = container_trigger
        self.header_type = header_type
        self.rx_accept_contained_i_pdu = rx_accept_contained_i_pdu


class MultiplexedIPdu(Pdu):
    def __init__(
            self,
            dynamic_parts: list[DynamicPart] | None = None,
            selector_field_byte_order: str | None = None,
            selector_field_length: int | None = None,
            selector_field_start_position: int | None = None,
            static_parts: list | None = None,
            trigger_mode: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if dynamic_parts is None:
            dynamic_parts = []
        self.dynamic_parts = dynamic_parts
        self.selector_field_byte_order = selector_field_byte_order
        if selector_field_length is None:
            selector_field_length = 0
        self.selector_field_length = selector_field_length
        if selector_field_start_position is None:
            selector_field_start_position = 0
        self.selector_field_start_position = selector_field_start_position
        if static_parts is None:
            static_parts = []
        self.static_parts = static_parts
        self.trigger_mode = trigger_mode


class SecuredIPdu(Pdu):
    def __init__(
            self,
            contained_i_pdu_props: ContainedIPduProps | None = None,
            authentication_props_ref: str | None = None,
            freshness_props_ref: str | None = None,
            payload_ref: str | None = None,
            secure_communication_props: SecureCommunicationProps | None = None,
            use_as_cryptographic_i_pdu: bool = False,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.contained_i_pdu_props = contained_i_pdu_props
        self.authentication_props_ref = authentication_props_ref
        self.freshness_props_ref = freshness_props_ref
        self.payload_ref = payload_ref
        self.secure_communication_props = secure_communication_props
        self.use_as_cryptographic_i_pdu = use_as_cryptographic_i_pdu


class GeneralPurposeIPdu(GeneralPurposePdu):
    pass


class SoConIPduIdentifier(Element):
    def __init__(
            self,
            header_id: int | None = None,
            pdu_triggering_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.header_id = header_id
        self.pdu_triggering_ref = pdu_triggering_ref


class SocketConnectionIPduIdentifierSet(Element):
    def __init__(
            self,
            i_pdu_identifiers: Iterable[SoConIPduIdentifier] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.i_pdu_identifiers = self._set_parent(i_pdu_identifiers)
        self._find_sets = [self.i_pdu_identifiers]
