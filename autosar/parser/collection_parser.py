from xml.etree.ElementTree import Element

from autosar import ArObject
from autosar.collection import Collection
from autosar.parser.parser_base import ElementParser


class CollectionParser(ElementParser):
    def get_supported_tags(self):
        return ['COLLECTION']

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> Collection | None:
        if xml_element.tag == 'COLLECTION':
            return self._parse_collection(xml_element, parent)
        return None

    def _parse_collection(self, xml_elem: Element, parent: ArObject | None) -> Collection | None:
        role = None
        refs = []
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'ELEMENT-ROLE':
                    role = self.parse_text_node(child_elem)
                case 'ELEMENT-REFS':
                    for sub_elem in child_elem.findall('./*'):
                        if sub_elem.tag != 'ELEMENT-REF':
                            self._logger.error(f'Unexpected tag for {child_elem.tag}: {sub_elem.tag}')
                        ref = self.parse_text_node(sub_elem)
                        if ref is not None:
                            refs.append(ref)
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        common_args = self._parse_common_tags(xml_elem)
        if common_args['name'] is None:
            self._logger.warning(f'Cannot find <SHORT-NAME> in {xml_elem.tag}, skipping')
            return None
        collection = Collection(
            element_role=role,
            element_refs=refs,
            parent=parent,
            **common_args,
        )
        return collection
