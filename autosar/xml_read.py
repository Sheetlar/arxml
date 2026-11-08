from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree

from autosar.misc import not_none
from autosar.model.package import Package
from autosar.model.system import System
from autosar.parser.admin_data_parser import AdminDataParser
from autosar.parser.package_parser import BetterPackageParser
from autosar.top_level import Autosar
from autosar.workspace import get_xml_namespace, remove_namespace


def model_from_xml(xml_root: Element) -> Autosar:
    def parse_package(ar_package: Element) -> Package | None:
        pp = BetterPackageParser()
        package = pp.parse_element(ar_package)
        found_systems.extend(pp.found_systems)
        return package

    ad_parser = AdminDataParser()
    admin_data = ad_parser.parse_element(xml_root.find('ADMIN-DATA'))
    ar_packages = xml_root.findall('AR-PACKAGES/AR-PACKAGE')
    found_systems: list[System] = []
    return Autosar(
        packages=filter(not_none, map(parse_package, ar_packages)),
        admin_data=admin_data,
        systems=found_systems,
    )


def read_model_xml(xml_file: Path) -> Autosar:
    arxml_tree = ElementTree()
    arxml_tree.parse(xml_file)
    arxml_root = arxml_tree.getroot()
    if arxml_root is None:
        raise ValueError('Missing root element in ARXML file')
    ns = get_xml_namespace(arxml_root)
    if ns is not None:
        remove_namespace(arxml_root, ns)
    return model_from_xml(arxml_root)
