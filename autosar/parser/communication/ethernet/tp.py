from xml.etree.ElementTree import Element

from autosar.model.communication.ethernet.frame_tp import EthTpConnection, EthTpConfig
from autosar.parser.communication.tp_base import TpConnectionParser, TpConfigParser
from autosar.parser.parser_base import handler, multiple_with_check


class EthTpConnectionParser(TpConnectionParser[EthTpConnection]):
    _returned_type = EthTpConnection

    @handler('TP-SDU-REFS')
    @multiple_with_check
    def _parse_tp_sdu(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class EthTpConfigParser(TpConfigParser[EthTpConfig]):
    _returned_type = EthTpConfig

    @handler('TP-CONNECTIONS')
    @multiple_with_check(expected_name='ETH-TP-CONNECTION')
    def _parse_tp_connections(self, xml_element: Element) -> EthTpConnection | None:
        parser = EthTpConnectionParser()
        return parser.parse_element(xml_element)
