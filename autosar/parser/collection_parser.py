from xml.etree.ElementTree import Element

from autosar.model.collection import Collection
from autosar.model.enums import AutoCollectEnum
from autosar.model.instance_ref import AnyInstanceRef
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.instance_ref_parser import AnyInstRefParser
from autosar.parser.parser_base import handler, multiple_with_check


class CollectionParser(IdentifiableParser[Collection]):
    _returned_type = Collection

    @handler('AUTO-COLLECT')
    def _parse_auto_collect(self, xml_element: Element) -> AutoCollectEnum | None:
        return self._parse_enum_node(xml_element, AutoCollectEnum)

    @handler('COLLECTION-SEMANTICS')
    def _parse_collection_semantics(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ELEMENT-ROLE')
    def _parse_element_role(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ELEMENT-REFS')
    @multiple_with_check
    def _parse_element(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SOURCE-ELEMENT-REFS')
    @multiple_with_check
    def _parse_source_element(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('COLLECTED-INSTANCE-IREF', param='collected_instance')
    def _parse_collected_instance(self, xml_element: Element) -> AnyInstanceRef | None:
        parser = AnyInstRefParser()
        return parser.parse_element(xml_element)

    @handler('SOURCE-INSTANCE-IREFS', param='source_instances')
    @multiple_with_check
    def _parse_source_instance(self, xml_element: Element) -> AnyInstanceRef | None:
        parser = AnyInstRefParser()
        return parser.parse_element(xml_element)
