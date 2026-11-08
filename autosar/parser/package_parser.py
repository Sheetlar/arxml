from xml.etree.ElementTree import Element

from autosar.misc import HasLogger
from autosar.model.element import Element as ArElement
from autosar.model.package import Package
from autosar.model.system import System
from autosar.parser.element_parser import ElementParserSelector
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import ElementParser, handler, multiple_with_check, not_implemented_handler


class PackageParser(HasLogger):
    def __init__(self, version: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert (isinstance(version, float))
        self.version = version
        self.registered_parsers: dict[str, ElementParser] = {}
        self.switcher: dict[str, ElementParser] = {}

    def register_element_parser(self, element_parser: ElementParser):
        """
        Registers a new element parser into the package parser
        """
        assert (isinstance(element_parser, ElementParser))
        name = type(element_parser).__name__
        if name not in self.registered_parsers:
            for tag_name in element_parser.get_supported_tags():
                self.switcher[tag_name] = element_parser
            self.registered_parsers[name] = element_parser


class BetterPackageParser(IdentifiableParser[Package]):
    _returned_type = Package

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.found_systems: list[System] = []

    @handler('AR-PACKAGES', param='packages')
    @multiple_with_check
    def _parse_package(self, xml_element: Element) -> Package | None:
        pp = BetterPackageParser()
        package = pp.parse_element(xml_element)
        self.found_systems.extend(pp.found_systems)
        return package

    @handler('ELEMENTS')
    def _parse_elements(self, xml_element: Element) -> list[ArElement]:
        elements: list[ArElement] = []
        not_implemented: set[str] = set()
        unexpected: set[str] = set()
        for child in xml_element:
            try:
                parser = ElementParserSelector(child.tag)
                if (e := parser.parse_element(child)) is not None:
                    elements.append(e)
                    if isinstance(e, System):
                        self.found_systems.append(e)
            except NotImplementedError:
                not_implemented.add(child.tag)
            except NameError:
                unexpected.add(child.tag)
        if len(not_implemented) > 0:
            self._logger.warning(f'Parser not implemented for element subclasses {self._tag_list(not_implemented)}')
        if len(unexpected) > 0:
            self._logger.warning(f'Unexpected tags in {xml_element.tag}: {self._tag_list(unexpected)}')
        return elements

    @not_implemented_handler('REFERENCE-BASES')
    def _parse_ref_bases(self, xml_element: Element):
        ...
