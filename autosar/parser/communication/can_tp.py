from xml.etree.ElementTree import Element

from autosar.model.communication.can import (
    CanTpAddress,
    CanTpChannel,
    CanTpConnection,
    CanTpEcu,
    CanTpNode,
    CanTpConfig,
)
from autosar.model.enums import (
    CanTpAddressingFormatType,
    NetworkTargetAddressType,
    CanTpChannelModeType,
)
from autosar.parser.communication.tp_base import TpConnectionParser, TpConfigParser
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import handler, multiple_with_check, BasicParser


class CanTpAddressParser(IdentifiableParser[CanTpAddress]):
    _returned_type = CanTpAddress

    @handler('TP-ADDRESS', required=True)
    def _parse_tp_address(self, xml_element: Element) -> int:
        if (addr := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return addr

    @handler('TP-ADDRESS-EXTENSION-VALUE')
    def _parse_tp_address_extension_value(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class CanTpChannelParser(IdentifiableParser[CanTpChannel]):
    _returned_type = CanTpChannel

    @handler('CHANNEL-ID')
    def _parse_channel_id(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('CHANNEL-MODE')
    def _parse_channel_mode(self, xml_element: Element) -> CanTpChannelModeType | None:
        return self._parse_enum_node(xml_element, CanTpChannelModeType)


class CanTpConnectionParser(TpConnectionParser[CanTpConnection]):
    _returned_type = CanTpConnection

    @handler('ADDRESSING-FORMAT', required=True)
    def _parse_addressing_format(self, xml_element: Element) -> CanTpAddressingFormatType:
        if (af := self._parse_enum_node(xml_element, CanTpAddressingFormatType)) is None:
            raise ValueError
        return af

    @handler('CAN-TP-CHANNEL-REF', required=True)
    def _parse_can_tp_channel(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('DATA-PDU-REF', required=True)
    def _parse_data_pdu(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('PADDING-ACTIVATION', required=True)
    def _parse_padding_activation(self, xml_element: Element) -> bool:
        if (pa := self._parse_boolean_node(xml_element)) is None:
            raise ValueError
        return pa

    @handler('TP-SDU-REF', required=True)
    def _parse_tp_sdu(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('CANCELLATION')
    def _parse_cancellation(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('FLOW-CONTROL-PDU-REF')
    def _parse_flow_control_pdu(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('MAX-BLOCK-SIZE')
    def _parse_max_block_size(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('MULTICAST-REF')
    def _parse_multicast(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('RECEIVER-REFS')
    @multiple_with_check
    def _parse_receiver(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TA-TYPE')
    def _parse_ta_type(self, xml_element: Element) -> NetworkTargetAddressType | None:
        return self._parse_enum_node(xml_element, NetworkTargetAddressType)

    @handler('TIMEOUT-BR')
    def _parse_timeout_br(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('TIMEOUT-BS')
    def _parse_timeout_bs(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('TIMEOUT-CR')
    def _parse_timeout_cr(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('TIMEOUT-CS')
    def _parse_timeout_cs(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('TRANSMITTER-REF')
    def _parse_transmitter(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class CanTpEcuParser(BasicParser[CanTpEcu]):
    _returned_type = CanTpEcu

    @handler('ECU-INSTANCE-REF', required=True)
    def _parse_ecu_instance(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref

    @handler('CYCLE-TIME-MAIN-FUNCTION')
    def _parse_cycle_time_main_function(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class CanTpNodeParser(IdentifiableParser[CanTpNode]):
    _returned_type = CanTpNode

    @handler('CONNECTOR-REF')
    def _parse_connector(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TP-ADDRESS-REF')
    def _parse_tp_address(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('MAX-FC-WAIT')
    def _parse_max_fc_wait(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('ST-MIN')
    def _parse_st_min(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('TIMEOUT-AR')
    def _parse_timeout_ar(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('TIMEOUT-AS')
    def _parse_timeout_as(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class CanTpConfigParser(TpConfigParser[CanTpConfig]):
    _returned_type = CanTpConfig

    @handler('TP-ADDRESSES', 'TP-ADDRESSS')
    @multiple_with_check(expected_name='TP-ADDRESS')
    def _parse_tp_address(self, xml_element: Element) -> CanTpAddress | None:
        parser = CanTpAddressParser()
        return parser.parse_element(xml_element)

    @handler('TP-CHANNELS')
    @multiple_with_check
    def _parse_tp_channel(self, xml_element: Element) -> CanTpChannel | None:
        parser = CanTpChannelParser()
        return parser.parse_element(xml_element)

    @handler('TP-CONNECTIONS')
    @multiple_with_check
    def _parse_tp_connection(self, xml_element: Element) -> CanTpConnection | None:
        parser = CanTpConnectionParser()
        return parser.parse_element(xml_element)

    @handler('TP-ECUS')
    @multiple_with_check
    def _parse_tp_ecu(self, xml_element: Element) -> CanTpEcu | None:
        parser = CanTpEcuParser()
        return parser.parse_element(xml_element)

    @handler('TP-NODES')
    @multiple_with_check
    def _parse_tp_node(self, xml_element: Element) -> CanTpNode | None:
        parser = CanTpNodeParser()
        return parser.parse_element(xml_element)
