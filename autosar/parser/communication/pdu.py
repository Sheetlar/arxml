from typing import TypeVar
from xml.etree.ElementTree import Element

from autosar.model.communication.pdu import (
    Pdu,
    IPdu,
    GeneralPurposePdu,
    NmPdu,
    UserDefinedPdu,
    ContainerIPdu,
    DcmIPdu,
    GeneralPurposeIPdu,
    ISignalIPdu,
    J1939DcmIPdu,
    J1939ProtectedIPdu,
    MultiplexedIPdu,
    NPdu,
    SecuredIPdu,
    UserDefinedIPdu,
    ISignalToIPduMapping,
    IPduTiming,
    MultiplexedPart,
    DynamicPart,
    StaticPart,
    SegmentPosition,
    DynamicPartAlternative,
    SecureCommunicationProps,
    ContainedIPduProps,
    ISignalIPduGroup,
    PdurIPduGroup,
    GeneralPurposeConnection,
)
from autosar.model.enums import (
    ContainerIPduTriggerEnum,
    ContainerIPduHeaderTypeEnum,
    RxAcceptContainedIPduEnum,
    SecuredPduHeaderEnum,
    TriggerMode,
    DiagPduType,
    ByteOrderEnum,
    ContainedIPduCollectionSemanticsEnum,
    PduCollectionTriggerEnum,
    TransferPropertyEnum,
    CommunicationDirectionType,
)
from autosar.parser.communication.pdu_timing import IPduTimingParser
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    eval_children,
    ref_variation,
    BasicParser,
)

MP = TypeVar('MP', bound=MultiplexedPart)
P = TypeVar('P', bound=Pdu)
IP = TypeVar('IP', bound=IPdu)


class ISignalToIPduMappingParser(IdentifiableParser[ISignalToIPduMapping]):
    _returned_type = ISignalToIPduMapping

    @handler('I-SIGNAL-REF')
    def _parse_i_signal(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('I-SIGNAL-GROUP-REF')
    def _parse_i_signal_group(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PACKING-BYTE-ORDER')
    def _parse_packing_byte_order(self, xml_element: Element) -> ByteOrderEnum | None:
        return self._parse_enum_node(xml_element, ByteOrderEnum)

    @handler('TRANSFER-PROPERTY')
    def _parse_transfer_property(self, xml_element: Element) -> TransferPropertyEnum | None:
        return self._parse_enum_node(xml_element, TransferPropertyEnum)

    @handler('START-POSITION')
    def _parse_start_position(self, xml_element: Element) -> int:
        return self._parse_int_node(xml_element) or 0

    @handler('UPDATE-INDICATION-BIT-POSITION')
    def _parse_update_indication_bit_position(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class SecureCommunicationPropsParser(BasicParser[SecureCommunicationProps]):
    _returned_type = SecureCommunicationProps

    @handler('DATA-ID', required=True)
    def _parse_data_id(self, xml_element: Element) -> int:
        if (id_ := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return id_

    @handler('AUTH-DATA-FRESHNESS-LENGTH')
    def _parse_auth_data_freshness_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('AUTH-DATA-FRESHNESS-START-POSITION')
    def _parse_auth_data_freshness_start_position(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('FRESHNESS-VALUE-ID')
    def _parse_freshness_value_id(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SECONDARY-FRESHNESS-VALUE-ID')
    def _parse_secondary_freshness_value_id(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('AUTHENTICATION-BUILD-ATTEMPTS')
    def _parse_authentication_build_attempts(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('AUTHENTICATION-RETRIES')
    def _parse_authentication_retries(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MESSAGE-LINK-LENGTH')
    def _parse_message_link_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MESSAGE-LINK-POSITION')
    def _parse_message_link_position(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SECURED-AREA-LENGTH')
    def _parse_secured_area_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SECURED-AREA-OFFSET')
    def _parse_secured_area_offset(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class ContainedIPduPropsParser(BasicParser[ContainedIPduProps]):
    _returned_type = ContainedIPduProps

    @handler('COLLECTION-SEMANTICS', required=True)
    def _parse_collection_semantics(self, xml_element: Element) -> ContainedIPduCollectionSemanticsEnum:
        if (cs := self._parse_enum_node(xml_element, ContainedIPduCollectionSemanticsEnum)) is None:
            raise ValueError
        return cs

    @handler('CONTAINED-PDU-TRIGGERING-REF')
    def _parse_contained_pdu_triggering_ref(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('HEADER-ID-LONG-HEADER')
    def _parse_header_id_long_header(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('HEADER-ID-SHORT-HEADER')
    def _parse_header_id_short_header(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('J-1939-REQUESTABLE')
    def _parse_j1939_requestable(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('OFFSET')
    def _parse_offset(self, xml_element: Element) -> int:
        return self._parse_int_node(xml_element) or 0

    @handler('PRIORITY')
    def _parse_priority(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('TIMEOUT')
    def _parse_timeout(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('TRIGGER')
    def _parse_trigger(self, xml_element: Element) -> PduCollectionTriggerEnum | None:
        return self._parse_enum_node(xml_element, PduCollectionTriggerEnum)

    @handler('UPDATE-INDICATION-BIT-POSITION')
    def _parse_update_indication_bit_position(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class SegmentPositionParser(BasicParser[SegmentPosition]):
    _returned_type = SegmentPosition

    @handler('SEGMENT-BYTE-ORDER', required=True)
    def _parse_segment_byte_order(self, xml_element: Element) -> ByteOrderEnum:
        if (bo := self._parse_enum_node(xml_element, ByteOrderEnum)) is None:
            raise ValueError
        return bo

    @handler('SEGMENT-LENGTH', required=True)
    def _parse_segment_length(self, xml_element: Element) -> int:
        if (length := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return length

    @handler('SEGMENT-POSITION', required=True)
    def _parse_segment_position(self, xml_element: Element) -> int:
        if (pos := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return pos


class DynamicPartAlternativeParser(BasicParser[DynamicPartAlternative]):
    _returned_type = DynamicPartAlternative

    @handler('I-PDU-REF', required=True)
    def _parse_i_pdu(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('INITIAL-DYNAMIC-PART', required=True)
    def _parse_initial_dynamic_part(self, xml_element: Element) -> bool:
        if (init := self._parse_boolean_node(xml_element)) is None:
            raise ValueError
        return init

    @handler('SELECTOR-FIELD-CODE', required=True)
    def _parse_selector_field_code(self, xml_element: Element) -> int:
        if (code := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return code


class MultiplexedPartParser(BasicParser[MP]):
    @handler('SEGMENT-POSITIONS', required=True)
    @eval_children
    @multiple_with_check
    def _parse_segment_position(self, xml_element: Element) -> SegmentPosition | None:
        parser = SegmentPositionParser()
        return parser.parse_element(xml_element)


class DynamicPartParser(MultiplexedPartParser[DynamicPart]):
    _returned_type = DynamicPart

    @handler('DYNAMIC-PART-ALTERNATIVES')
    @eval_children
    @multiple_with_check
    def _parse_dynamic_part_alternative(self, xml_element: Element) -> DynamicPartAlternative | None:
        parser = DynamicPartAlternativeParser()
        return parser.parse_element(xml_element)


class StaticPartParser(MultiplexedPartParser[StaticPart]):
    _returned_type = StaticPart

    @handler('I-PDU-REF', required=True)
    def _parse_i_pdu(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref


class PduParser(IdentifiableParser[P]):
    @handler('LENGTH', required=True)
    def _parse_length(self, xml_element: Element) -> int:
        if (length := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return length

    @handler('HAS-DYNAMIC-LENGTH')
    def _parse_has_dynamic_length(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)


class GeneralPurposePduParser(PduParser[GeneralPurposePdu]):
    _returned_type = GeneralPurposePdu


class NmPduParser(PduParser[NmPdu]):
    _returned_type = NmPdu

    @handler('NM-DATA-INFORMATION')
    def _parse_nm_data_information(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('NM-VOTE-INFORMATION')
    def _parse_nm_vote_information(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('UNUSED-BIT-PATTERN')
    def _parse_unused_bit_pattern(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('I-SIGNAL-TO-I-PDU-MAPPINGS')
    @multiple_with_check
    def _parse_i_signal_to_i_pdu_mapping(self, xml_element: Element) -> ISignalToIPduMapping | None:
        parser = ISignalToIPduMappingParser()
        return parser.parse_element(xml_element)


class UserDefinedPduParser(PduParser[UserDefinedPdu]):
    _returned_type = UserDefinedPdu

    @handler('CDD-TYPE')
    def _parse_cdd_type(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class IPduParser(PduParser[IP]):
    @handler('CONTAINED-I-PDU-PROPS')
    def _parse_contained_i_pdu_props(self, xml_element: Element) -> ContainedIPduProps | None:
        parser = ContainedIPduPropsParser()
        return parser.parse_element(xml_element)


class ContainerIPduParser(IPduParser[ContainerIPdu]):
    _returned_type = ContainerIPdu

    @handler('HEADER-TYPE', required=True)
    def _parse_header_type(self, xml_element: Element) -> ContainerIPduHeaderTypeEnum:
        if (header := self._parse_enum_node(xml_element, ContainerIPduHeaderTypeEnum)) is None:
            raise ValueError
        return header

    @handler('RX-ACCEPT-CONTAINED-I-PDU', required=True)
    def _parse_rx_accept_contained_i_pdu(self, xml_element: Element) -> RxAcceptContainedIPduEnum:
        if (accept := self._parse_enum_node(xml_element, RxAcceptContainedIPduEnum)) is None:
            raise ValueError
        return accept

    @handler('CONTAINED-I-PDU-TRIGGERING-PROPSS', param='contained_i_pdu_triggering_props')
    @multiple_with_check(expected_name='CONTAINED-I-PDU-PROPS')
    def _parse_contained_i_pdu_triggering_props(self, xml_element: Element) -> ContainedIPduProps | None:
        parser = ContainedIPduPropsParser()
        return parser.parse_element(xml_element)

    @handler('CONTAINED-PDU-TRIGGERING-REFS')
    @multiple_with_check
    def _parse_contained_pdu_triggering(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTAINER-TIMEOUT')
    def _parse_container_timeout(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('CONTAINER-TRIGGER')
    def _parse_container_trigger(self, xml_element: Element) -> ContainerIPduTriggerEnum | None:
        return self._parse_enum_node(xml_element, ContainerIPduTriggerEnum)

    @handler('MINIMUM-RX-CONTAINER-QUEUE-SIZE')
    def _parse_minimum_rx_container_queue_size(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MINIMUM-TX-CONTAINER-QUEUE-SIZE')
    def _parse_minimum_tx_container_queue_size(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('THRESHOLD-SIZE')
    def _parse_threshold_size(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('UNUSED-BIT-PATTERN')
    def _parse_unused_bit_pattern(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class DcmIPduParser(IPduParser[DcmIPdu]):
    _returned_type = DcmIPdu

    @handler('DIAG-PDU-TYPE', required=True)
    def _parse_diag_pdu_type(self, xml_element: Element) -> DiagPduType:
        if (t := self._parse_enum_node(xml_element, DiagPduType)) is None:
            raise ValueError
        return t


class GeneralPurposeIPduParser(IPduParser[GeneralPurposeIPdu]):
    _returned_type = GeneralPurposeIPdu


class ISignalIPduParser(IPduParser[ISignalIPdu]):
    _returned_type = ISignalIPdu

    @handler('I-SIGNAL-TO-PDU-MAPPINGS')
    @multiple_with_check(expected_name='I-SIGNAL-TO-I-PDU-MAPPING')
    def _parse_i_signal_to_pdu_mapping(self, xml_element: Element) -> ISignalToIPduMapping | None:
        parser = ISignalToIPduMappingParser()
        return parser.parse_element(xml_element)

    @handler('I-PDU-TIMING-SPECIFICATIONS')
    @multiple_with_check(expected_name='I-PDU-TIMING')
    def _parse_i_pdu_timing_specification(self, xml_element: Element) -> IPduTiming | None:
        parser = IPduTimingParser()
        return parser.parse_element(xml_element)

    @handler('UNUSED-BIT-PATTERN')
    def _parse_unused_bit_pattern(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class J1939DcmIPduParser(IPduParser[J1939DcmIPdu]):
    _returned_type = J1939DcmIPdu

    @handler('DIAGNOSTIC-MESSAGE-TYPE')
    def _parse_diagnostic_message_type(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class J1939ProtectedIPduParser(IPduParser[J1939ProtectedIPdu]):
    _returned_type = J1939ProtectedIPdu

    @handler('PAYLOADS', param='payload_refs')
    @ref_variation(element_name='PDU-TRIGGERING')
    def _parse_payload(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SRVT')
    def _parse_srvt(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class MultiplexedIPduParser(IPduParser[MultiplexedIPdu]):
    _returned_type = MultiplexedIPdu

    @handler('SELECTOR-FIELD-BYTE-ORDER')
    def _parse_selector_field_byte_order(self, xml_element: Element) -> ByteOrderEnum | None:
        return self._parse_enum_node(xml_element, ByteOrderEnum)

    @handler('SELECTOR-FIELD-LENGTH')
    def _parse_selector_field_length(self, xml_element: Element) -> int:
        return self._parse_int_node(xml_element) or 0

    @handler('SELECTOR-FIELD-START-POSITION')
    def _parse_selector_field_start_position(self, xml_element: Element) -> int:
        return self._parse_int_node(xml_element) or 0

    @handler('DYNAMIC-PARTS')
    @multiple_with_check
    def _parse_dynamic_part(self, xml_element: Element) -> DynamicPart | None:
        parser = DynamicPartParser()
        return parser.parse_element(xml_element)

    @handler('STATIC-PARTS')
    @multiple_with_check
    def _parse_static_part(self, xml_element: Element) -> StaticPart | None:
        parser = StaticPartParser()
        return parser.parse_element(xml_element)

    @handler('TRIGGER-MODE')
    def _parse_trigger_mode(self, xml_element: Element) -> TriggerMode | None:
        return self._parse_enum_node(xml_element, TriggerMode)

    @handler('UNUSED-BIT-PATTERN')
    def _parse_unused_bit_pattern(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class NPduParser(IPduParser[NPdu]):
    _returned_type = NPdu


class SecuredIPduParser(IPduParser[SecuredIPdu]):
    _returned_type = SecuredIPdu

    @handler('PAYLOAD-REF', required=True)
    def _parse_payload(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('SECURE-COMMUNICATION-PROPS', required=True)
    def _parse_secure_communication_props(self, xml_element: Element) -> SecureCommunicationProps:
        parser = SecureCommunicationPropsParser()
        if (props := parser.parse_element(xml_element)) is None:
            raise ValueError
        return props

    @handler('AUTHENTICATION-PROPS-REF')
    def _parse_authentication_props(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('FRESHNESS-PROPS-REF')
    def _parse_freshness_props(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('DYNAMIC-RUNTIME-LENGTH-HANDLING')
    def _parse_dynamic_runtime_length_handling(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('USE-AS-CRYPTOGRAPHIC-I-PDU')
    def _parse_use_as_cryptographic_i_pdu(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('USE-SECURED-PDU-HEADER')
    def _parse_use_secured_pdu_header(self, xml_element: Element) -> SecuredPduHeaderEnum | None:
        return self._parse_enum_node(xml_element, SecuredPduHeaderEnum)


class UserDefinedIPduParser(PduParser[UserDefinedIPdu]):
    _returned_type = UserDefinedIPdu

    @handler('CDD-TYPE')
    def _parse_cdd_type(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class ISignalIPduGroupParser(IdentifiableParser[ISignalIPduGroup]):
    _returned_type = ISignalIPduGroup

    @handler('COMMUNICATION-DIRECTION', required=True)
    def _parse_communication_direction(self, xml_element: Element) -> CommunicationDirectionType:
        if (cd := self._parse_enum_node(xml_element, CommunicationDirectionType)) is None:
            raise ValueError
        return cd

    @handler('COMMUNICATION-MODE')
    def _parse_communication_mode(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTAINED-I-SIGNAL-I-PDU-GROUP-REFS')
    @multiple_with_check
    def _parse_contained_i_signal_i_pdu_group(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('I-SIGNAL-I-PDUS', param='i_signal_i_pdu_refs')
    @ref_variation
    def _parse_i_signal_i_pdu(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('NM-PDUS', param='nm_pdu_refs')
    @ref_variation
    def _parse_nm_pdu(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class PdurIPduGroupParser(IdentifiableParser[PdurIPduGroup]):
    _returned_type = PdurIPduGroup

    @handler('COMMUNICATION-MODE')
    def _parse_communication_mode(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('I-PDUS', param='nm_pdu_refs')
    @ref_variation(element_name='PDU-TRIGGERING')
    def _parse_i_pdu(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class GeneralPurposeConnectionParser(IdentifiableParser[GeneralPurposeConnection]):
    _returned_type = GeneralPurposeConnection

    @handler('PDU-TRIGGERING-REFS')
    @multiple_with_check
    def _parse_pdu_triggering(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)
