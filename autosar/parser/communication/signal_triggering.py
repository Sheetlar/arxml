from xml.etree.ElementTree import Element

from autosar.model.communication.signal import ISignalTriggering
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import handler, multiple_with_check


class ISignalTriggeringParser(IdentifiableParser[ISignalTriggering]):
    _returned_type = ISignalTriggering

    @handler('I-SIGNAL-REF')
    def _parse_i_signal(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('I-SIGNAL-GROUP-REF')
    def _parse_i_signal_group(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('I-SIGNAL-PORT-REFS')
    @multiple_with_check
    def _parse_signal_port(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)
