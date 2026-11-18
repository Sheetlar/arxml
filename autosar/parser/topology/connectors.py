from typing import TypeVar
from xml.etree.ElementTree import Element

from autosar.model.base import DataFilter
from autosar.model.topology.ethernet import EthernetCommunicationConnector
from autosar.model.topology.flexray import FlexrayCommunicationConnector
from autosar.model.topology.can import CanCommunicationConnector
from autosar.model.topology.lin import LinConfigurableFrame, LinOrderedConfigurableFrame, LinCommunicationConnector
from autosar.model.topology.abstract import CommConnectorPort, CommunicationConnector, FramePort, IPduPort, ISignalPort
from autosar.model.topology.user_defined import UserDefinedCommunicationConnector
from autosar.model.enums import (
    CommunicationDirectionType,
    IPduSignalProcessingEnum,
    HandleInvalidEnum,
    PncGatewayTypeEnum,
)
from autosar.parser.common_simple_parsers import DataFilterParser
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    multiple,
    ref_variation,
    ParserSelector,
    BasicParser,
)

CP = TypeVar('CP', bound=CommConnectorPort)
CC = TypeVar('CC', bound=CommunicationConnector)


class CommPortParser(IdentifiableParser[CP]):
    @handler('COMMUNICATION-DIRECTION', required=True)
    def _parse_communication_direction(self, xml_element: Element) -> CommunicationDirectionType:
        direction = self._parse_enum_node(xml_element, CommunicationDirectionType)
        if direction is None:
            raise ValueError
        return direction


class FramePortParser(CommPortParser[FramePort]):
    _returned_type = FramePort


class IPduPortParser(CommPortParser[IPduPort]):
    _returned_type = IPduPort

    @handler('I-PDU-SIGNAL-PROCESSING')
    def _parse_i_pdu_signal_processing(self, xml_element: Element) -> IPduSignalProcessingEnum | None:
        return self._parse_enum_node(xml_element, IPduSignalProcessingEnum)

    @handler('TIMESTAMP-RX-ACCEPTANCE-WINDOW')
    def _parse_timestamp_rx_acceptance_window(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('RX-SECURITY-VERIFICATION')
    def _parse_rx_security_verification(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('USE-AUTH-DATA-FRESHNESS')
    def _parse_use_auth_data_freshness(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)


class ISignalPortParser(CommPortParser[ISignalPort]):
    _returned_type = ISignalPort

    @handler('DATA-FILTER')
    def _parse_data_filter(self, xml_element: Element) -> DataFilter | None:
        parser = DataFilterParser()
        return parser.parse_element(xml_element)

    @handler('HANDLE-INVALID')
    def _parse_handle_invalid(self, xml_element: Element) -> HandleInvalidEnum | None:
        return self._parse_enum_node(xml_element, HandleInvalidEnum)

    @handler('FIRST-TIMEOUT')
    def _parse_first_timeout(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('TIMEOUT')
    def _parse_timeout(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('DDS-QOS-PROFILE-REF')
    def _parse_dds_qos_profile(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class CommPortParserSelector(ParserSelector[CP]):
    _tag_map = {
        'FRAME-PORT': FramePortParser,
        'I-PDU-PORT': IPduPortParser,
        'I-SIGNAL-PORT': ISignalPortParser,
    }


class LinConfigurableFrameParser(BasicParser[LinConfigurableFrame]):
    _returned_type = LinConfigurableFrame

    @handler('FRAME-REF', required=True)
    def _parse_frame(self, xml_element: Element) -> str:
        ref = self._parse_text_node(xml_element)
        if ref is None:
            raise ValueError
        return ref

    @handler('MESSAGE-ID')
    def _parse_message_id(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class LinOrderedConfigurableFrameParser(BasicParser[LinOrderedConfigurableFrame]):
    _returned_type = LinOrderedConfigurableFrame

    @handler('FRAME-REF', required=True)
    def _parse_frame(self, xml_element: Element) -> str:
        ref = self._parse_text_node(xml_element)
        if ref is None:
            raise ValueError
        return ref

    @handler('INDEX', required=True)
    def _parse_index(self, xml_element: Element) -> int:
        index = self._parse_int_node(xml_element)
        if index is None:
            raise ValueError
        return index


class CommunicationConnectorParser(IdentifiableParser[CC]):  # Abstract
    @handler('COMM-CONTROLLER-REF', required=True)
    def _parse_comm_controller(self, xml_element: Element) -> str | None:
        ref = self._parse_text_node(xml_element)
        if ref is None:
            raise ValueError
        return ref

    @handler('ECU-COMM-PORT-INSTANCES')
    @multiple
    def _parse_ecu_comm_port_instance(self, xml_element: Element) -> CP | None:
        parser = CommPortParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('CREATE-ECU-WAKEUP-SOURCE')
    def _parse_create_ecu_wakeup_source(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('DYNAMIC-PNC-TO-CHANNEL-MAPPING-ENABLED')
    def _parse_dynamic_pnc_to_channel_mapping_enabled(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('EXPLICIT-WAKEUP-CHANNEL-REFS', param='explicit_wakeup_channel_refs')
    @ref_variation(element_name='PHYSICAL-CHANNEL')
    def _parse_explicit_wakeup_channel(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('EXPLICIT-WAKEUP-PNC-REFS', param='explicit_wakeup_pnc_refs')
    @ref_variation(element_name='PNC-MAPPING-IDENT')
    def _parse_explicit_wakeup_pnc(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PNC-FILTER-ARRAY-MASKS')
    @multiple_with_check
    def _parse_pnc_filter_array_mask(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PNC-GATEWAY-TYPE')
    def _parse_pnc_gateway_type(self, xml_element: Element) -> PncGatewayTypeEnum | None:
        return self._parse_enum_node(xml_element, PncGatewayTypeEnum)


class CanCommunicationConnectorParser(
    CommunicationConnectorParser[CanCommunicationConnector]
):
    _returned_type = CanCommunicationConnector

    @handler('PNC-WAKEUP-CAN-ID')
    def _parse_pnc_wakeup_can_id(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PNC-WAKEUP-CAN-ID-MASK')
    def _parse_pnc_wakeup_can_id_mask(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PNC-WAKEUP-DATA-MASK')
    def _parse_pnc_wakeup_data_mask(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PNC-WAKEUP-DLC')
    def _parse_pnc_wakeup_dlc(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PNC-WAKEUP-CAN-ID-EXTENDED')
    def _parse_pnc_wakeup_can_id_extended(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)


class EthernetCommunicationConnectorParser(
    CommunicationConnectorParser[EthernetCommunicationConnector]
):
    _returned_type = EthernetCommunicationConnector

    @handler('ETH-IP-PROPS-REF')
    def _parse_eth_ip_props(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('MAXIMUM-TRANSMISSION-UNIT')
    def _parse_maximum_transmission_unit(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('NEIGHBOR-CACHE-SIZE')
    def _parse_neighbor_cache_size(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PATH-MTU-ENABLED')
    def _parse_path_mtu_enabled(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('PATH-MTU-TIMEOUT')
    def _parse_path_mtu_timeout(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class FlexrayCommunicationConnectorParser(
    CommunicationConnectorParser[FlexrayCommunicationConnector]
):
    _returned_type = FlexrayCommunicationConnector

    @handler('NM-READY-SLEEP-TIME')
    def _parse_nm_ready_sleep_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('WAKE-UP-CHANNEL')
    def _parse_wake_up_channel(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)


class LinCommunicationConnectorParser(
    CommunicationConnectorParser[LinCommunicationConnector]
):
    _returned_type = LinCommunicationConnector

    @handler('LIN-CONFIGURABLE-FRAMES')
    @multiple_with_check
    def _parse_lin_configurable_frame(self, xml_element: Element) -> LinConfigurableFrame | None:
        parser = LinConfigurableFrameParser()
        return parser.parse_element(xml_element)

    @handler('LIN-ORDERED-CONFIGURABLE-FRAMES')
    @multiple_with_check
    def _parse_lin_ordered_configurable_frame(self, xml_element: Element) -> LinOrderedConfigurableFrame | None:
        parser = LinOrderedConfigurableFrameParser()
        return parser.parse_element(xml_element)

    @handler('SCHEDULE-CHANGE-NEXT-TIME-BASE')
    def _parse_schedule_change_next_time_base(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)


class UserDefinedCommunicationConnectorParser(
    CommunicationConnectorParser[UserDefinedCommunicationConnector]
):
    _returned_type = UserDefinedCommunicationConnector


class CommunicationConnectorParserSelector(ParserSelector[CC]):
    _tag_map = {
        'CAN-COMMUNICATION-CONNECTOR': CanCommunicationConnectorParser,
        'ETHERNET-COMMUNICATION-CONNECTOR': EthernetCommunicationConnectorParser,
        'FLEXRAY-COMMUNICATION-CONNECTOR': FlexrayCommunicationConnectorParser,
        'LIN-COMMUNICATION-CONNECTOR': LinCommunicationConnectorParser,
        'USER-DEFINED-COMMUNICATION-CONNECTOR': UserDefinedCommunicationConnectorParser,
    }
