from xml.etree.ElementTree import Element

from autosar.model.communication.some_ip import (
    SoConIPduIdentifier,
    SocketConnectionIPduIdentifierSet,
)
from autosar.model.enums import PduCollectionSemanticsEnum, PduCollectionTriggerEnum
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
