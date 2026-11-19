from xml.etree.ElementTree import Element

from autosar.model.communication.some_ip import (
    SoConIPduIdentifier,
    SocketConnectionIPduIdentifierSet,
    SomeIpTpChannel,
    SomeIpTpConnection,
    SomeIpTpConfig,
)
from autosar.model.enums import PduCollectionSemanticsEnum, PduCollectionTriggerEnum
from autosar.parser.communication.tp_base import TpConfigParser
from autosar.parser.identifiable import IdentifiableParser, ReferrableParser
from autosar.parser.parser_base import (
    handler,
    not_implemented_handler,
    multiple_with_check,
    multiple,
    eval_children,
    ref_variation,
    single_subclass_aggr,
    BasicParser,
    ParserSelector,
)


class SoConIPduIdentifierParser(ReferrableParser[SoConIPduIdentifier]):
    _returned_type = SoConIPduIdentifier

    @handler('HEADER-ID')
    def _parse_header_id(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PDU-TRIGGERING-REF')
    def _parse_pdu_triggering(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PDU-COLLECTION-PDU-TIMEOUT')
    def _parse_pdu_collection_pdu_timeout(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('PDU-COLLECTION-SEMANTICS')
    def _parse_pdu_collection_semantics(self, xml_element: Element) -> PduCollectionSemanticsEnum | None:
        return self._parse_enum_node(xml_element, PduCollectionSemanticsEnum)

    @handler('PDU-COLLECTION-TRIGGER')
    def _parse_pdu_collection_trigger(self, xml_element: Element) -> PduCollectionTriggerEnum | None:
        return self._parse_enum_node(xml_element, PduCollectionTriggerEnum)


class SocketConnectionIPduIdentifierSetParser(
    IdentifiableParser[SocketConnectionIPduIdentifierSet]
):
    _returned_type = SocketConnectionIPduIdentifierSet

    @handler('I-PDU-IDENTIFIERS')
    @multiple_with_check(expected_name='SO-CON-I-PDU-IDENTIFIER')
    def _parse_i_pdu_identifier(self, xml_element: Element) -> SoConIPduIdentifier | None:
        parser = SoConIPduIdentifierParser()
        return parser.parse_element(xml_element)


class SomeIpTpChannelParser(IdentifiableParser[SomeIpTpChannel]):
    _returned_type = SomeIpTpChannel

    @handler('BURST-SIZE')
    def _parse_burst_size(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('RX-TIMEOUT-TIME')
    def _parse_rx_timeout_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)

    @handler('SEPARATION-TIME')
    def _parse_separation_time(self, xml_element: Element) -> float | None:
        return self._parse_float_node(xml_element)


class SomeIpTpConnectionParser(BasicParser[SomeIpTpConnection]):
    _returned_type = SomeIpTpConnection

    @handler('TP-CHANNEL-REF')
    def _parse_tp_channel_ref(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TP-SDU-REF')
    def _parse_tp_sdu_ref(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TRANSPORT-PDU-REF')
    def _parse_transport_pdu_ref(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TP-CONCURRENT-PROCESSING-SDUS', param='tp_concurrent_processing_sdu_refs')
    @ref_variation
    def _parse_tp_concurrent_processing_sdu(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class SomeIpTpConfigParser(TpConfigParser[SomeIpTpConfig]):
    _returned_type = SomeIpTpConfig

    @handler('TP-CHANNELS')
    @multiple_with_check(expected_name='SOMEIP-TP-CHANNEL')
    def _parse_tp_channel(self, xml_element: Element) -> SomeIpTpChannel | None:
        parser = SomeIpTpChannelParser()
        return parser.parse_element(xml_element)

    @handler('TP-CONNECTIONS')
    @multiple_with_check(expected_name='SOMEIP-TP-CONNECTION')
    def _parse_tp_connection(self, xml_element: Element) -> SomeIpTpConnection | None:
        parser = SomeIpTpConnectionParser()
        return parser.parse_element(xml_element)
