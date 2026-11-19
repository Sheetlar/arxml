from xml.etree.ElementTree import Element

from autosar.model.communication.do_ip import (
    DoIpLogicTargetAddressProps,
    DoIpLogicTesterAddressProps,
    DoIpLogicAddressProps,
    DoIpLogicAddress,
    DoIpRoutingActivation,
    DoIpTpConnection,
    DoIpTpConfig,
    DoIpInterface,
    DoIpConfig,
)
from autosar.parser.communication.tp_base import TpConnectionParser, TpConfigParser
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    single_subclass_aggr,
    BasicParser,
    ParserSelector,
)


class DoIpLogicTargetAddressPropsParser(IdentifiableParser[DoIpLogicTargetAddressProps]):
    _returned_type = DoIpLogicTargetAddressProps


class DoIpLogicTesterAddressPropsParser(IdentifiableParser[DoIpLogicTesterAddressProps]):
    _returned_type = DoIpLogicTesterAddressProps

    @handler('DO-IP-TESTER-ROUTING-ACTIVATION-REFS')
    @multiple_with_check
    def _parse_do_ip_tester_routing_activation(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class DoIpLogicAddressPropsParserSelector(ParserSelector[DoIpLogicAddressProps]):
    _tag_map = {
        'DO-IP-LOGIC-TARGET-ADDRESS-PROPS': DoIpLogicTargetAddressPropsParser,
        'DO-IP-LOGIC-TESTER-ADDRESS-PROPS': DoIpLogicTesterAddressPropsParser,
    }


class DoIpLogicAddressParser(IdentifiableParser[DoIpLogicAddress]):
    _returned_type = DoIpLogicAddress

    @handler('ADDRESS')
    def _parse_address(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('DO-IP-LOGIC-ADDRESS-PROPS')
    @single_subclass_aggr
    def _parse_do_ip_logic_address_props(self, xml_element: Element) -> DoIpLogicAddressProps | None:
        parser = DoIpLogicAddressPropsParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)


class DoIpRoutingActivationParser(IdentifiableParser[DoIpRoutingActivation]):
    _returned_type = DoIpRoutingActivation

    @handler('DO-IP-TARGET-ADDRESS-REFS')
    @multiple_with_check
    def _parse_do_ip_target_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class DoIpTpConnectionParser(TpConnectionParser[DoIpTpConnection]):
    _returned_type = DoIpTpConnection

    @handler('DO-IP-SOURCE-ADDRESS-REF', required=True)
    def _parse_do_ip_source_address(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('DO-IP-TARGET-ADDRESS-REF', required=True)
    def _parse_do_ip_target_address(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('TP-SDU-REF', required=True)
    def _parse_tp_sdu(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref


class DoIpTpConfigParser(TpConfigParser[DoIpTpConfig]):
    _returned_type = DoIpTpConfig

    @handler('TP-CONNECTIONS', required=True)
    @multiple_with_check(expected_name='DO-IP-TP-CONNECTION')
    def _parse_tp_connection(self, xml_element: Element) -> DoIpTpConnection | None:
        parser = DoIpTpConnectionParser()
        return parser.parse_element(xml_element)

    @handler('DO-IP-LOGIC-ADDRESSES', 'DO-IP-LOGIC-ADDRESSS')
    @multiple_with_check(expected_name='DO-IP-LOGIC-ADDRESS')
    def _parse_do_ip_logic_address(self, xml_element: Element) -> DoIpLogicAddress | None:
        parser = DoIpLogicAddressParser()
        return parser.parse_element(xml_element)


class DoIpInterfaceParser(IdentifiableParser[DoIpInterface]):
    _returned_type = DoIpInterface

    @handler('ALIVE-CHECK-RESPONSE-TIMEOUT')
    def _parse_alive_check_response_timeout(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('DOIP-CHANNEL-COLLECTION-REF')
    def _parse_doip_channel_collection(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('DO-IP-ROUTING-ACTIVATIONS')
    @multiple_with_check
    def _parse_do_ip_routing_activation(self, xml_element: Element) -> DoIpRoutingActivation | None:
        parser = DoIpRoutingActivationParser()
        return parser.parse_element(xml_element)

    @handler('GENERAL-INACTIVITY-TIME')
    def _parse_general_inactivity_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('INITIAL-INACTIVITY-TIME')
    def _parse_initial_inactivity_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('INITIAL-VEHICLE-ANNOUNCEMENT-TIME')
    def _parse_initial_vehicle_announcement_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('IS-ACTIVATION-LINE-DEPENDENT')
    def _parse_is_activation_line_dependent(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('MAX-TESTER-CONNECTIONS')
    def _parse_max_tester_connections(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('SOCKET-CONNECTION-REFS')
    @multiple_with_check
    def _parse_socket_connection(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('USE-MAC-ADDRESS-FOR-IDENTIFICATION')
    def _parse_use_mac_address_for_identification(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('USE-VEHICLE-IDENTIFICATION-SYNC-STATUS')
    def _parse_use_vehicle_identification_sync_status(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('VEHICLE-ANNOUNCEMENT-COUNT')
    def _parse_vehicle_announcement_count(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('VEHICLE-ANNOUNCEMENT-INTERVAL')
    def _parse_vehicle_announcement_interval(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class DoIpConfigParser(BasicParser[DoIpConfig]):
    _returned_type = DoIpConfig

    @handler('DOIP-INTERFACES')
    @multiple_with_check(expected_name='DO-IP-INTERFACE')
    def _parse_doip_interface(self, xml_element: Element) -> DoIpInterface | None:
        parser = DoIpInterfaceParser()
        return parser.parse_element(xml_element)

    @handler('DO-IP-PROTOCOL-VERSION')
    def _parse_do_ip_protocol_version(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('LOGIC-ADDRESS')
    def _parse_logic_address(self, xml_element: Element) -> DoIpLogicAddress | None:
        parser = DoIpLogicAddressParser()
        return parser.parse_element(xml_element)
