from xml.etree.ElementTree import Element

from autosar.model.communication.communication_cluster import TriggerIPduSendCondition, PduTriggering
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import BasicParser, handler, eval_children, multiple_with_check, ref_variation


class TriggerIPduSendConditionParser(BasicParser[TriggerIPduSendCondition]):
    _returned_type = TriggerIPduSendCondition

    @handler('MODE-DECLARATION-REFS')
    @eval_children
    @multiple_with_check
    def _parse_mode_declaration(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class PduTriggeringParser(IdentifiableParser[PduTriggering]):
    _returned_type = PduTriggering

    @handler('I-PDU-REF')
    def _parse_i_pdu(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('I-PDU-PORT-REFS')
    @multiple_with_check
    def _parse_signal_port(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('I-SIGNAL-TRIGGERINGS', param='i_signal_triggering_refs')
    @ref_variation
    def _parse_signal_triggering(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SEC-OC-CRYPTO-MAPPING-REF')
    def _parse_crypto_mapping(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SEC-OC-CRYPTO-SERVICE-MAPPING', param='sec_oc_crypto_service_mapping_refs')
    @ref_variation
    def _parse_crypto_service_mapping(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TRIGGER-I-PDU-SEND-CONDITIONS')
    @multiple_with_check
    def _parse_send_condition(self, xml_element: Element) -> TriggerIPduSendCondition | None:
        parser = TriggerIPduSendConditionParser()
        return parser.parse_element(xml_element)
