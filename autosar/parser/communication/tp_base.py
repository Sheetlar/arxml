from typing import TypeVar
from xml.etree.ElementTree import Element

from autosar.model.transport_protocol import (
    TpConnectionIdent,
    TpConnection,
    TpAddress,
    TpConfig,
)
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

TPC = TypeVar('TPC', bound=TpConnection)
TPA = TypeVar('TPA', bound=TpAddress)
TC = TypeVar('TC', bound=TpConfig)


class TpConnectionIdentParser(ReferrableParser[TpConnectionIdent]):
    _returned_type = TpConnectionIdent


class TpConnectionParser(BasicParser[TPC]):
    @handler('IDENT')
    def _parse_ident(self, xml_element: Element) -> TpConnectionIdent | None:
        parser = TpConnectionIdentParser()
        return parser.parse_element(xml_element)


class TpAddressParser(IdentifiableParser[TPA]):
    @handler('TP-ADDRESS', required=True)
    def _parse_tp_address(self, xml_element: Element) -> int:
        if (addr := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return addr


class TpConfigParser(IdentifiableParser[TC]):
    @handler('COMMUNICATION-CLUSTER-REF', required=True)
    def _parse_communication_cluster(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref
