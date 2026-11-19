from xml.etree.ElementTree import Element

from autosar.model.communication.ethernet.endpoint import (
    ApplicationEndpoint,
    AnyTcpUdpConfig,
    UdpTp,
    TcpTp,
    TpPort,
)
from autosar.model.communication.ethernet.socket import StaticSocketConnection, SocketAddress, SoAdConfig
from autosar.model.enums import TcpRoleEnum, UdpChecksumCalculationEnum
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    single_subclass_aggr,
    BasicParser,
    ParserSelector, ref_variation,
)


class TpPortParser(BasicParser[TpPort]):
    _returned_type = TpPort

    @handler('PORT-NUMBER')
    def _parse_port_number(self, xml_element: Element) -> int:
        return self._parse_int_node(xml_element) or 0

    @handler('DYNAMICALLY-ASSIGNED')
    def _parse_dynamically_assigned(self, xml_element: Element) -> bool:
        return self._parse_boolean_node(xml_element) or False


class UdpTpParser(BasicParser[UdpTp]):
    _returned_type = UdpTp

    @handler('UDP-TP-PORT', required=True)
    def _parse_udp_tp_port(self, xml_element: Element) -> TpPort:
        parser = TpPortParser()
        port = parser.parse_element(xml_element)
        if port is None:
            raise ValueError
        return port


class TcpTpParser(BasicParser[TcpTp]):
    _returned_type = TcpTp

    @handler('TCP-TP-PORT', required=True)
    def _parse_tcp_tp_port(self, xml_element: Element) -> TpPort:
        parser = TpPortParser()
        port = parser.parse_element(xml_element)
        if port is None:
            raise ValueError
        return port

    @handler('KEEP-ALIVE-INTERVAL')
    def _parse_keep_alive_interval(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('KEEP-ALIVE-PROBES-MAX')
    def _parse_keep_alive_probes_max(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('KEEP-ALIVE-TIME')
    def _parse_keep_alive_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('KEEP-ALIVES')
    def _parse_keep_alives(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('NAGLES-ALGORITHM')
    def _parse_nagles_algorithm(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('RECEIVE-WINDOW-MIN')
    def _parse_receive_window_min(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('TCP-RETRANSMISSION-TIMEOUT')
    def _parse_tcp_retransmission_timeout(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class TcpUdpConfigParserSelector(ParserSelector[AnyTcpUdpConfig]):
    _tag_map = {
        'UDP-TP': UdpTpParser,
        'TCP-TP': TcpTpParser,
    }


class ApplicationEndpointParser(IdentifiableParser[ApplicationEndpoint]):
    _returned_type = ApplicationEndpoint

    @handler('NETWORK-ENDPOINT-REF', required=True)
    def _parse_network_endpoint(self, xml_element: Element) -> str:
        ref = self._parse_text_node(xml_element)
        if ref is None:
            raise ValueError
        return ref

    @handler('TP-CONFIGURATION')
    @single_subclass_aggr
    def _parse_tp_configuration(self, xml_element: Element) -> AnyTcpUdpConfig | None:
        parser = TcpUdpConfigParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('MAX-NUMBER-OF-CONNECTIONS')
    def _parse_max_number_of_connections(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PRIORITY')
    def _parse_priority(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('TLS-CRYPTO-MAPPING-REF')
    def _parse_tls_crypto_mapping(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class StaticSocketConnectionParser(IdentifiableParser[StaticSocketConnection]):
    _returned_type = StaticSocketConnection

    @handler('I-PDU-IDENTIFIERS', param='i_pdu_identifier_refs')
    @ref_variation(element_name='SO-CON-I-PDU-IDENTIFIER')
    def _parse_i_pdu_identifier(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('REMOTE-ADDRESSES', 'REMOTE-ADDRESSS', param='remote_address_refs')
    @ref_variation(element_name='SOCKET-ADDRESS')
    def _parse_remote_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TCP-CONNECT-TIMEOUT')
    def _parse_tcp_connect_timeout(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('TCP-ROLE')
    def _parse_tcp_role(self, xml_element: Element) -> TcpRoleEnum | None:
        return self._parse_enum_node(xml_element, TcpRoleEnum)


class SocketAddressParser(IdentifiableParser[SocketAddress]):
    _returned_type = SocketAddress

    @handler('ALLOWED-IPV-6-EXT-HEADERS-REF')
    def _parse_allowed_ipv6_ext_headers(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ALLOWED-TCP-OPTIONS-REF')
    def _parse_allowed_tcp_options(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('APPLICATION-ENDPOINT')
    def _parse_application_endpoint(self, xml_element: Element) -> ApplicationEndpoint | None:
        parser = ApplicationEndpointParser()
        return parser.parse_element(xml_element)

    @handler('CONNECTOR-REF')
    def _parse_connector(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('DIFFERENTIATED-SERVICE-FIELD')
    def _parse_differentiated_service_field(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('FLOW-LABEL')
    def _parse_flow_label(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MULTICAST-CONNECTOR-REFS')
    @multiple_with_check
    def _parse_multicast_connector(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PATH-MTU-DISCOVERY-ENABLED')
    def _parse_path_mtu_discovery_enabled(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('PDU-COLLECTION-MAX-BUFFER-SIZE')
    def _parse_pdu_collection_max_buffer_size(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PDU-COLLECTION-TIMEOUT')
    def _parse_pdu_collection_timeout(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('STATIC-SOCKET-CONNECTIONS')
    @multiple_with_check
    def _parse_static_socket_connection(self, xml_element: Element) -> StaticSocketConnection | None:
        parser = StaticSocketConnectionParser()
        return parser.parse_element(xml_element)

    @handler('TTL')
    def _parse_ttl(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('UDP-CHECKSUM-HANDLING')
    def _parse_udp_checksum_handling(self, xml_element: Element) -> UdpChecksumCalculationEnum | None:
        return self._parse_enum_node(xml_element, UdpChecksumCalculationEnum)


class SoAdConfigParser(BasicParser[SoAdConfig]):
    _returned_type = SoAdConfig

    @handler('SOCKET-ADDRESSES', 'SOCKET-ADDRESSS')
    @multiple_with_check(expected_name='SOCKET-ADDRESS')
    def _parse_socket_address(self, xml_element: Element) -> SocketAddress | None:
        parser = SocketAddressParser()
        return parser.parse_element(xml_element)
