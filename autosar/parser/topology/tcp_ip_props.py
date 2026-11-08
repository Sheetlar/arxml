from xml.etree.ElementTree import Element

from autosar.model.topology.tcp_ip_props import UdpProps, TcpProps, EthTcpIpProps
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import handler, BasicParserWithoutParent


class TcpPropsParser(BasicParserWithoutParent[TcpProps]):
    _returned_type = TcpProps

    @handler('TCP-CONGESTION-AVOIDANCE-ENABLED')
    def _parse_tcp_congestion_avoidance_enabled(self, xml_element: Element) -> bool:
        return self._parse_boolean_node(xml_element) or False

    @handler('TCP-DELAYED-ACK-TIMEOUT')
    def _parse_tcp_delayed_ack_timeout(self, xml_element: Element) -> int | float | None:
        return self._parse_number_node(xml_element)

    @handler('TCP-FAST-RECOVERY-ENABLED')
    def _parse_tcp_fast_recovery_enabled(self, xml_element: Element) -> bool:
        return self._parse_boolean_node(xml_element) or False

    @handler('TCP-FAST-RETRANSMIT-ENABLED')
    def _parse_tcp_fast_retransmit_enabled(self, xml_element: Element) -> bool:
        return self._parse_boolean_node(xml_element) or False

    @handler('TCP-FIN-WAIT-2-TIMEOUT')
    def _parse_tcp_fin_wait_2_timeout(self, xml_element: Element) -> int | float | None:
        return self._parse_number_node(xml_element)

    @handler('TCP-KEEP-ALIVE-ENABLED')
    def _parse_tcp_keep_alive_enabled(self, xml_element: Element) -> bool:
        return self._parse_boolean_node(xml_element) or False

    @handler('TCP-KEEP-ALIVE-INTERVAL')
    def _parse_tcp_keep_alive_interval(self, xml_element: Element) -> int | float | None:
        return self._parse_number_node(xml_element)

    @handler('TCP-KEEP-ALIVE-PROBES-MAX')
    def _parse_tcp_keep_alive_probes_max(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('TCP-KEEP-ALIVE-TIME')
    def _parse_tcp_keep_alive_time(self, xml_element: Element) -> int | float | None:
        return self._parse_number_node(xml_element)

    @handler('TCP-MAX-RTX')
    def _parse_tcp_max_rtx(self, xml_element: Element) -> int | float | None:
        return self._parse_number_node(xml_element)

    @handler('TCP-MSL')
    def _parse_tcp_msl(self, xml_element: Element) -> int | float | None:
        return self._parse_number_node(xml_element)

    @handler('TCP-NAGLE-ENABLED')
    def _parse_tcp_nagle_enabled(self, xml_element: Element) -> bool:
        return self._parse_boolean_node(xml_element) or False

    @handler('TCP-RECEIVE-WINDOW-MAX')
    def _parse_tcp_receive_window_max(self, xml_element: Element) -> int | float | None:
        return self._parse_number_node(xml_element)

    @handler('TCP-RETRANSMISSION-TIMEOUT')
    def _parse_tcp_retransmission_timeout(self, xml_element: Element) -> int | float | None:
        return self._parse_number_node(xml_element)

    @handler('TCP-SLOW-START-ENABLED')
    def _parse_tcp_slow_start_enabled(self, xml_element: Element) -> bool:
        return self._parse_boolean_node(xml_element) or False

    @handler('TCP-SYN-MAX-RTX')
    def _parse_tcp_syn_max_rtx(self, xml_element: Element) -> int | float | None:
        return self._parse_number_node(xml_element)

    @handler('TCP-SYN-RECEIVED-TIMEOUT')
    def _parse_tcp_syn_received_timeout(self, xml_element: Element) -> int | float | None:
        return self._parse_number_node(xml_element)

    @handler('TCP-TTL')
    def _parse_tcp_ttl(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class UdpPropsParser(BasicParserWithoutParent[UdpProps]):
    _returned_type = UdpProps

    @handler('TCP-TTL')
    def _parse_tcp_ttl(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class EthTcpIpPropsParser(IdentifiableParser[EthTcpIpProps]):
    _returned_type = EthTcpIpProps

    @handler('TCP-PROPS')
    def _parse_tcp_props(self, xml_element: Element) -> TcpProps | None:
        parser = TcpPropsParser()
        return parser.parse_element(xml_element)

    @handler('UDP-PROPS')
    def _parse_udp_props(self, xml_element: Element) -> UdpProps | None:
        parser = UdpPropsParser()
        return parser.parse_element(xml_element)
