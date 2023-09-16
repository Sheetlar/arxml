from typing import Callable
from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.mode import ModeDeclaration, ModeDeclarationGroup
from autosar.parser.parser_base import ElementParser


class ModeDeclarationParser(ElementParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 3.0 <= self.version < 4.0:
            self.switcher: dict[str, Callable[[Element, ArObject | None], ModeDeclarationGroup | list[ModeDeclaration]]] = {
                'MODE-DECLARATION-GROUP': self.parse_mode_declaration_group,
                'MODE-DECLARATIONS': self.parse_mode_declarations,
            }
        elif self.version >= 4.0:
            self.switcher: dict[str, Callable[[Element, ArObject | None], ModeDeclarationGroup]] = {
                'MODE-DECLARATION-GROUP': self.parse_mode_declaration_group,
            }

    def get_supported_tags(self):
        return self.switcher.keys()

    def parse_element(
            self,
            xml_element: Element,
            parent: ArObject | None = None,
    ) -> ModeDeclarationGroup | list[ModeDeclaration] | None:
        parse_func = self.switcher.get(xml_element.tag)
        if parse_func is not None:
            return parse_func(xml_element, parent)
        return None

    def parse_mode_declaration_group(self, xml_root: Element, parent: ArObject | None) -> ModeDeclarationGroup:
        assert (xml_root.tag == 'MODE-DECLARATION-GROUP')
        name = self.parse_text_node(xml_root.find('./SHORT-NAME'))
        category = self.parse_text_node(xml_root.find('./CATEGORY'))
        initial_mode_ref = self.parse_text_node(xml_root.find('./INITIAL-MODE-REF'))
        mode_declaration_group = ModeDeclarationGroup(
            name,
            initial_mode_ref,
            None,
            parent=parent,
        )
        if xml_root.find('./MODE-DECLARATIONS') is not None:
            self.parse_mode_declarations(xml_root.find('./MODE-DECLARATIONS'), mode_declaration_group)
        if self.has_admin_data(xml_root):
            admin_data = self.parse_admin_data_node(xml_root.find('ADMIN-DATA'))
            mode_declaration_group.admin_data = admin_data
        if category is not None:
            mode_declaration_group.category = category
        return mode_declaration_group

    def parse_mode_declarations(self, xml_root: Element, parent: ArObject | None) -> list[ModeDeclaration]:
        assert (xml_root.tag == 'MODE-DECLARATIONS')
        assert (isinstance(parent, ModeDeclarationGroup))
        result = []
        for mode in xml_root.findall('./MODE-DECLARATION'):
            declaration_name = self.parse_text_node(mode.find('./SHORT-NAME'))
            declaration_value = None
            declaration_value_xml = mode.find('./VALUE')
            if declaration_value_xml is not None:
                declaration_value = self.parse_text_node(declaration_value_xml)
            parent.mode_declarations.append(ModeDeclaration(
                declaration_name,
                declaration_value,
                parent=parent,
            ))
        return result
