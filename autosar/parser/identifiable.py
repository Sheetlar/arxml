from typing import TypeVar
from xml.etree.ElementTree import Element

from autosar.model.admin_data import AdminData
from autosar.model.base import ShortNameFragment, LangStr, Referrable, Identifiable, Describable
from autosar.parser.admin_data_parser import AdminDataParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    not_implemented_handler,
    BasicParser,
)


R = TypeVar('R', bound=Referrable)
ID = TypeVar('ID', bound=Identifiable)
D = TypeVar('D', bound=Describable)


class ReferrableParser(BasicParser[R]):
    @handler('SHORT-NAME', param='name', required=True)
    def _parse_name(self, xml_element: Element) -> str:
        name = self._parse_text_node(xml_element)
        if name is None:
            raise ValueError
        return name

    @handler('SHORT-NAME-FRAGMENTS')
    @multiple_with_check
    def _parse_sn_fragment(self, xml_element: Element) -> ShortNameFragment | None:
        fragment = self._parse_text_node(xml_element.find('FRAGMENT'))
        if fragment is None:
            self.log_missing_required(xml_element, 'FRAGMENT')
            return None
        role = self._parse_text_node(xml_element.find('ROLE'))
        if role is None:
            self.log_missing_required(xml_element, 'ROLE')
            return None
        return ShortNameFragment(fragment, role)


class IdentifiableParser(ReferrableParser[ID]):
    _valid_categories: set[str] | None = None

    def _parse_attributes(self, xml_element: Element) -> dict[str, str | None]:
        return {'uuid': xml_element.attrib.get('UUID', None)}

    @handler('ADMIN-DATA')
    def _parse_admin_data(self, xml_element: Element) -> AdminData | None:
        parser = AdminDataParser()
        return parser.parse_element(xml_element)

    @handler('DESC')
    def _parse_desc(self, xml_element: Element) -> LangStr | None:
        return self._parse_lang_string(xml_element, l_num=2)

    @handler('LONG-NAME')
    def _parse_long_name(self, xml_element: Element) -> LangStr | None:
        return self._parse_lang_string(xml_element, l_num=4)

    @handler('CATEGORY')
    def _parse_category(self, xml_element: Element) -> str | None:
        cat = self._parse_text_node(xml_element)
        if self._valid_categories is not None and cat not in self._valid_categories:
            self._logger.warning(f'Category {cat} is not valid for {self._returned_type}, '
                                 f'possible values: {self._tag_list(self._valid_categories)}')
        return cat

    @not_implemented_handler('ANNOTATION')
    def _parse_annotation(self, xml_element: Element):
        ...

    @not_implemented_handler('INTRODUCTION')
    def _parse_introduction(self, xml_element: Element):
        ...


class DescribableParser(BasicParser[D]):
    _valid_categories: set[str] | None = None

    @handler('ADMIN-DATA')
    def _parse_admin_data(self, xml_element: Element) -> AdminData | None:
        parser = AdminDataParser()
        return parser.parse_element(xml_element)

    @handler('DESC')
    def _parse_desc(self, xml_element: Element) -> LangStr | None:
        return self._parse_lang_string(xml_element, l_num=2)

    @handler('CATEGORY')
    def _parse_long_name(self, xml_element: Element) -> str | None:
        cat = self._parse_text_node(xml_element)
        if self._valid_categories is not None and cat not in self._valid_categories:
            self._logger.warning(f'Category {cat} is not valid for {self._returned_type}, '
                                 f'possible values: {self._tag_list(self._valid_categories)}')
        return cat

    @not_implemented_handler('INTRODUCTION')
    def _parse_introduction(self, xml_element: Element):
        ...
