from dataclasses import dataclass
from typing import Iterable

from autosar.model.ar_object import ArObject
from autosar.model.base import Describable, DataFilter
from autosar.model.element import Element


@dataclass
class TimeRangeTypeTolerance(ArObject):
    pass


@dataclass
class AbsoluteTolerance(TimeRangeTypeTolerance):
    absolute: float


@dataclass
class RelativeTolerance(TimeRangeTypeTolerance):
    relative: int


@dataclass
class TimeRangeType(ArObject):
    value: float
    tolerance: TimeRangeTypeTolerance


class CyclicTiming(Describable):
    def __init__(
            self,
            time_period: TimeRangeType,
            time_offset: TimeRangeType | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.time_period = time_period
        self.time_offset = time_offset


class EventControlledTiming(Describable):
    def __init__(
            self,
            number_of_repetitions: int,
            repetition_period: TimeRangeType | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.number_of_repetitions = number_of_repetitions
        self.repetition_period = repetition_period


@dataclass
class TransmissionModeTiming(ArObject):
    cyclic_timing: CyclicTiming | None = None
    event_controlled_timing: EventControlledTiming | None = None


@dataclass
class TransmissionModeCondition(ArObject):
    data_filter: DataFilter
    i_signal_in_i_pdu_ref: str


@dataclass
class ModeDrivenTransmissionModeCondition(ArObject):
    mode_declaration_refs: list[str]


@dataclass
class TransmissionModeDeclaration(ArObject):
    mode_driven_false_conditions: list[ModeDrivenTransmissionModeCondition] = None
    mode_driven_true_conditions: list[ModeDrivenTransmissionModeCondition] = None
    transmission_mode_conditions: list[TransmissionModeCondition] = None
    transmission_mode_false_timing: TransmissionModeTiming | None = None
    transmission_mode_true_timing: TransmissionModeTiming | None = None

    def __post_init__(self):
        if self.mode_driven_false_conditions is None:
            self.mode_driven_false_conditions = []
        if self.mode_driven_true_conditions is None:
            self.mode_driven_true_conditions = []
        if self.transmission_mode_conditions is None:
            self.transmission_mode_conditions = []


@dataclass
class SecureCommunicationProps(ArObject):
    authentication_retries: int
    data_id: int
    auth_data_freshness_length: int | None = None
    auth_data_freshness_start_position: int | None = None
    authentication_build_attempts: int | None = None
    freshness_value_id: int | None = None
    message_link_length: int | None = None
    message_link_position: int | None = None
    secondary_freshness_value_id: int | None = None
    secured_area_length: int | None = None
    secured_area_offset: int | None = None


@dataclass
class ContainedIPduProps(ArObject):
    collection_semantics: str
    contained_pdu_triggering_ref: str | None = None
    header_id_long_header: int | None = None
    header_id_short_header: int | None = None
    offset: int | None = None
    priority: int | None = None
    timeout: float | None = None
    trigger: str | None = None
    update_indication_bit_position: int | None = None

    def __post_init__(self):
        if self.offset is None:
            self.offset = 0


@dataclass
class SegmentPosition(ArObject):
    segment_byte_order: str
    segment_length: int
    segment_position: int


@dataclass
class DynamicPartAlternative(ArObject):
    i_pdu_ref: str
    initial_dynamic_part: bool
    selector_field_code: int


@dataclass
class MultiplexedPart(ArObject):
    segment_positions: list[SegmentPosition]


@dataclass
class DynamicPart(MultiplexedPart):
    dynamic_part_alternatives: list[DynamicPartAlternative]


@dataclass
class StaticPart(MultiplexedPart):
    i_pdu_ref: str


class IPduTiming(Describable):
    def __init__(
            self,
            minimum_delay: float | None = None,
            transmission_mode_declaration: TransmissionModeDeclaration | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.minimum_delay = minimum_delay
        self.transmission_mode_declaration = transmission_mode_declaration


class ISignalToIPduMapping(Element):
    def __init__(
            self,
            i_signal_ref: str | None = None,
            i_signal_group_ref: str | None = None,
            packing_byte_order: str | None = None,
            start_position: int | None = None,
            transfer_property: str | None = None,
            update_indication_bit_position: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if start_position is None:
            start_position = 0
        self.i_signal_ref = i_signal_ref
        self.i_signal_group_ref = i_signal_group_ref
        self.packing_byte_order = packing_byte_order
        self.start_position = start_position
        self.transfer_property = transfer_property
        self.update_indication_bit_position = update_indication_bit_position


# Abstract
class Pdu(Element):
    def __init__(
            self,
            length: int | None = None,
            has_dynamic_length: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.length = length
        self.has_dynamic_length = has_dynamic_length


class GeneralPurposePdu(Pdu):
    pass


class NMPdu(Pdu):
    def __init__(
            self,
            nm_data_information: bool | None = None,
            nm_vote_information: bool | None = None,
            unused_bit_pattern: int | None = None,
            i_signal_to_i_pdu_mappings: Iterable[ISignalToIPduMapping] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.nm_data_information = nm_data_information
        self.nm_vote_information = nm_vote_information
        self.unused_bit_pattern = unused_bit_pattern
        self.i_signal_to_i_pdu_mappings = self._set_parent(i_signal_to_i_pdu_mappings)
        self._find_sets = (self.i_signal_to_i_pdu_mappings,)


class UserDefinedPdu(Pdu):
    def __init__(
            self,
            cdd_type: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.cdd_type = cdd_type


# Abstract
class IPdu(Pdu):
    def __init__(
            self,
            contained_i_pdu_props: ContainedIPduProps | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.contained_i_pdu_props = contained_i_pdu_props


class ContainerIPdu(IPdu):
    def __init__(
            self,
            contained_i_pdu_triggering_props: list[ContainedIPduProps] | None = None,
            contained_pdu_triggering_refs: list[str] | None = None,
            container_timeout: float | None = None,
            container_trigger: str | None = None,
            header_type: str | None = None,
            minimum_rx_container_queue_size: int | None = None,
            minimum_tx_container_queue_size: int | None = None,
            rx_accept_contained_i_pdu: str | None = None,
            threshold_size: int | None = None,
            unused_bit_pattern: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if contained_i_pdu_triggering_props is None:
            contained_i_pdu_triggering_props = []
        if contained_pdu_triggering_refs is None:
            contained_pdu_triggering_refs = []
        self.contained_i_pdu_triggering_props = contained_i_pdu_triggering_props
        self.contained_pdu_triggering_refs = contained_pdu_triggering_refs
        self.container_timeout = container_timeout
        self.container_trigger = container_trigger
        self.header_type = header_type
        self.minimum_rx_container_queue_size = minimum_rx_container_queue_size
        self.minimum_tx_container_queue_size = minimum_tx_container_queue_size
        self.rx_accept_contained_i_pdu = rx_accept_contained_i_pdu
        self.threshold_size = threshold_size
        self.unused_bit_pattern = unused_bit_pattern


class DcmIPdu(IPdu):
    def __init__(
            self,
            diag_pdu_type: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.diag_pdu_type = diag_pdu_type


class GeneralPurposeIPdu(IPdu):
    pass


class ISignalIPdu(IPdu):
    def __init__(
            self,
            unused_bit_pattern: int,
            i_pdu_timing_specifications: list[IPduTiming] | None = None,
            i_signal_to_pdu_mappings: Iterable[ISignalToIPduMapping] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if i_pdu_timing_specifications is None:
            i_pdu_timing_specifications = []
        self.unused_bit_pattern = unused_bit_pattern
        self.i_pdu_timing_specifications = i_pdu_timing_specifications
        self.i_signal_to_pdu_mappings = self._set_parent(i_signal_to_pdu_mappings)
        self._find_sets = (self.i_signal_to_pdu_mappings,)


class J1939DcmIPdu(IPdu):
    def __init__(
            self,
            diagnostic_message_type: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.diagnostic_message_type = diagnostic_message_type


class MultiplexedIPdu(IPdu):
    def __init__(
            self,
            selector_field_byte_order: str | None = None,
            selector_field_length: int | None = None,
            selector_field_start_position: int | None = None,
            dynamic_parts: list[DynamicPart] | None = None,
            static_parts: list[StaticPart] | None = None,
            trigger_mode: str | None = None,
            unused_bit_pattern: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if selector_field_length is None:
            selector_field_length = 0
        if selector_field_start_position is None:
            selector_field_start_position = 0
        if dynamic_parts is None:
            dynamic_parts = []
        if static_parts is None:
            static_parts = []
        self.selector_field_byte_order = selector_field_byte_order
        self.selector_field_length = selector_field_length
        self.selector_field_start_position = selector_field_start_position
        self.dynamic_parts = dynamic_parts
        self.static_parts = static_parts
        self.trigger_mode = trigger_mode
        self.unused_bit_pattern = unused_bit_pattern


class NPdu(IPdu):
    pass


class SecuredIPdu(IPdu):
    def __init__(
            self,
            payload_ref: str,
            secure_communication_props: SecureCommunicationProps,
            authentication_props_ref: str | None = None,
            freshness_props_ref: str | None = None,
            use_as_cryptographic_i_pdu: bool | None = None,
            dynamic_runtime_length_handling: bool | None = None,
            use_secured_pdu_header: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.payload_ref = payload_ref
        self.secure_communication_props = secure_communication_props
        self.authentication_props_ref = authentication_props_ref
        self.freshness_props_ref = freshness_props_ref
        self.use_as_cryptographic_i_pdu = use_as_cryptographic_i_pdu
        self.dynamic_runtime_length_handling = dynamic_runtime_length_handling
        self.use_secured_pdu_header = use_secured_pdu_header


class UserDefinedIPdu(IPdu):
    def __init__(
            self,
            cdd_type: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.cdd_type = cdd_type


class ISignalIPduGroup(Element):
    def __init__(
            self,
            communication_direction: str,
            communication_mode: str,
            contained_i_signal_i_pdu_group_refs: list[str] | None = None,
            i_signal_i_pdu_refs: list[str] | None = None,
            nm_pdu_refs: list[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if contained_i_signal_i_pdu_group_refs is None:
            contained_i_signal_i_pdu_group_refs = []
        if i_signal_i_pdu_refs is None:
            i_signal_i_pdu_refs = []
        if nm_pdu_refs is None:
            nm_pdu_refs = []
        self.communication_direction = communication_direction
        self.communication_mode = communication_mode
        self.contained_i_signal_i_pdu_group_refs = contained_i_signal_i_pdu_group_refs
        self.i_signal_i_pdu_refs = i_signal_i_pdu_refs
        self.nm_pdu_refs = nm_pdu_refs


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
