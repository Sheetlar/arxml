from typing import TypeAlias
from xml.etree.ElementTree import Element

from autosar.model.base import Limit
from autosar.model.gateway import Gateway
from autosar.model.topology.abstract import (
    AnyCommunicationController,
    AnyCommunicationConnector,
)
from autosar.model.topology.ecu import (
    EcuInstance,
    ClientIdRange,
    EcuPartition,
)
from autosar.model.topology.tcp_ip_props import EthTcpIpProps
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    not_implemented_handler,
    multiple_with_check,
    multiple,
    ref_variation,
    BasicParserWithoutParent,
)
from autosar.parser.topology.connectors import CommunicationConnectorParserSelector
from autosar.parser.topology.controllers import CommunicationControllerParserSelector

SupportedElement: TypeAlias = EcuInstance | EthTcpIpProps | Gateway


class EcuPartitionParser(IdentifiableParser[EcuPartition]):
    _returned_type = EcuPartition

    @handler('EXEC-IN-USER-MODE')
    def _parse_exec_in_user_mode(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)


class ClientIdRangeParser(BasicParserWithoutParent[ClientIdRange]):
    _returned_type = ClientIdRange

    @handler('LOWER-LIMIT', required=True)
    def _parse_lower_limit(self, xml_element: Element) -> Limit:
        limit = self._parse_limit(xml_element)
        if limit is None:
            raise ValueError
        return limit

    @handler('UPPER-LIMIT', required=True)
    def _parse_upper_limit(self, xml_element: Element) -> Limit:
        limit = self._parse_limit(xml_element)
        if limit is None:
            raise ValueError
        return limit


class EcuInstanceParser(IdentifiableParser[EcuInstance]):
    _returned_type = EcuInstance

    @handler('COMM-CONTROLLERS')
    @multiple
    def _parse_comm_controllers(self, xml_element: Element) -> AnyCommunicationController | None:
        parser = CommunicationControllerParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('CONNECTORS')
    @multiple
    def _parse_connectors(self, xml_element: Element) -> AnyCommunicationConnector | None:
        parser = CommunicationConnectorParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('PARTITIONS')
    @multiple_with_check(expected_name='ECU-PARTITION')
    def _parse_partitions(self, xml_element: Element) -> EcuPartition | None:
        parser = EcuPartitionParser()
        return parser.parse_element(xml_element)

    @handler('DIAGNOSTIC-ADDRESS')
    def _parse_diagnostic_address(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('ASSOCIATED-COM-I-PDU-GROUP-REFS')
    @multiple_with_check
    def _parse_associated_com_i_pdu_group(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ASSOCIATED-CONSUMED-PROVIDED-SERVICE-INSTANCE-GROUPS', param='associated_cp_si_group_refs')
    @ref_variation(element_name='CONSUMED-PROVIDED-SERVICE-INSTANCE-GROUP')
    def _parse_associated_cp_si_group(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ASSOCIATED-PDUR-I-PDU-GROUP-REFS')
    @multiple_with_check
    def _parse_associated_pdu_r_i_pdu_group(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CHANNEL-SYNCHRONOUS-WAKEUP')
    def _parse_channel_synchronous_wakeup(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('CLIENT-ID-RANGE')
    def _parse_client_id_range(self, xml_element: Element) -> ClientIdRange | None:
        parser = ClientIdRangeParser()
        return parser.parse_element(xml_element)

    @handler('COM-CONFIGURATION-GW-TIME-BASE')
    def _parse_com_configuration_gw_time_base(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('COM-CONFIGURATION-RX-TIME-BASE')
    def _parse_com_configuration_rx_time_base(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('COM-CONFIGURATION-TX-TIME-BASE')
    def _parse_com_configuration_tx_time_base(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('COM-ENABLE-MDT-FOR-CYCLIC-TRANSMISSION')
    def _parse_com_enable_mdt_for_cyclic_transmission(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('ETH-SWITCH-PORT-GROUP-DERIVATION')
    def _parse_eth_switch_port_group_derivation(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('ECU-TASK-PROXY-REFS')
    @multiple_with_check
    def _parse_ecu_task_proxy(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('FIREWALL-RULE-REFS')
    @multiple_with_check
    def _parse_firewall_rule(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PNC-NM-REQUEST')
    def _parse_pnc_nm_request(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('PNC-SYNCHRONOUS-WAKEUP')
    def _parse_pnc_synchronous_wakeup(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('PNC-PREPARE-SLEEP-TIMER')
    def _parse_pnc_prepare_sleep_timer(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('PN-RESET-TIME')
    def _parse_pn_reset_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('SLEEP-MODE-SUPPORTED')
    def _parse_sleep_mode_supported(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('TCP-IP-ICMP-PROPS-REF')
    def _parse_tcp_ip_icmp_props(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TCP-IP-PROPS-REF')
    def _parse_tcp_ip_props(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('V-2X-SUPPORTED', param='v2x_supported')
    def _parse_v2x_supported(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('WAKE-UP-OVER-BUS-SUPPORTED')
    def _parse_wake_up_over_bus_supported(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @not_implemented_handler('DLT-CONFIG')
    def _parse_dlt_config(self, xml_element: Element):
        ...

    @not_implemented_handler('DO-IP-CONFIG')  # param='doip_config'
    def _parse_doip_config(self, xml_element: Element):
        ...

    @not_implemented_handler('J-1939-NODE')  # param='j1939_node'
    def _parse_j1939_node(self, xml_element: Element):
        ...
