from autosar.base import parse_text_node
from autosar.element import Element
from autosar.has_logger import HasLogger
from autosar.package import Package
from autosar.parser.parser_base import ElementParser


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

    def load_xml(self, package: Package, xml_root):
        """
        Loads an XML package by repeatedly invoking its registered element parsers
        """
        assert (self.switcher is not None)
        if xml_root.find('ELEMENTS'):
            element_names = set([x.name for x in package.elements])
            for xml_element in xml_root.findall('./ELEMENTS/*'):
                parser_object = self.switcher.get(xml_element.tag)
                if parser_object is not None:
                    element = parser_object.parse_element(xml_element, package)
                    if element is None:
                        self._logger.warning(f'No return value: {xml_element.tag}')
                        continue
                    element.parent = package
                    if isinstance(element, Element):
                        if element.name not in element_names:
                            # ignore duplicated items
                            package.append(element)
                            element_names.add(element.name)
                    else:
                        raise ValueError(f'Parse error: {xml_element.tag}')
                else:
                    package.unhandled_parser.add(xml_element.tag)

        if 3.0 <= self.version < 4.0:
            if xml_root.find('SUB-PACKAGES'):
                for xml_package in xml_root.findall('./SUB-PACKAGES/AR-PACKAGE'):
                    name = xml_package.find("./SHORT-NAME").text
                    sub_package = Package(name)
                    package.append(sub_package)
                    self.load_xml(sub_package, xml_package)
        elif self.version >= 4.0:
            for sub_package_xml in xml_root.findall('./AR-PACKAGES/AR-PACKAGE'):
                name = parse_text_node(sub_package_xml.find("./SHORT-NAME"))
                sub_package = package.find(name)
                if sub_package is None:
                    sub_package = Package(name)
                    package.append(sub_package)
                self.load_xml(sub_package, sub_package_xml)
