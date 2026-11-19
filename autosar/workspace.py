import re
from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree

from autosar.model.ar_object import ArObject
from autosar.model.base import (
    parse_autosar_version_and_schema,
    parse_version_string,
)
from autosar.model.package import Package
from autosar.model.system import System
from autosar.parser.behavior_parser import BehaviorParser
from autosar.parser.component_parser import ComponentTypeParser
from autosar.parser.constant_parser import ConstantParser
from autosar.parser.datatype_parser import DataTypeParser, DataTypeSemanticsParser, DataTypeUnitsParser
from autosar.parser.mode_parser import ModeDeclarationParser
from autosar.parser.package_parser import PackageParser
from autosar.parser.portinterface_parser import PortInterfacePackageParser, SoftwareAddressMethodParser
from autosar.parser.swc_implementation_parser import SwcImplementationParser


class WorkspaceProfile:
    """
    A Workspace profile allows users to customize default settings and behaviors
    """

    def __init__(self):
        self.compu_method_suffix = ''
        self.data_constraint_suffix = '_DataConstr'
        self.error_handling_opt = False
        self.sw_calibration_access_default = 'NOT-ACCESSIBLE'
        self.mode_switch_enhanced_mode_default = False
        self.mode_switch_support_async_default = False
        self.mode_switch_auto_set_mode_group_ref = False
        self.sw_base_type_encoding_default = 'NONE'

    def __repr__(self):
        return self.__class__.__name__


class Workspace(ArObject):
    """
    An autosar workspace
    """
    autosar_platform_types = {
        '/AUTOSAR_Platform/BaseTypes/uint8': '>u1',
        '/AUTOSAR_Platform/BaseTypes/uint16': '>u2',
        '/AUTOSAR_Platform/BaseTypes/uint32': '>u4',
        '/AUTOSAR_Platform/BaseTypes/uint64': '>u8',
        '/AUTOSAR_Platform/BaseTypes/sint8': '>i1',
        '/AUTOSAR_Platform/BaseTypes/sint16': '>i2',
        '/AUTOSAR_Platform/BaseTypes/sint32': '>i4',
        '/AUTOSAR_Platform/BaseTypes/sint64': '>i8',
        '/AUTOSAR_Platform/BaseTypes/float32': '>f4',
        '/AUTOSAR_Platform/ImplementationDataTypes/uint8': '>u1',
        '/AUTOSAR_Platform/ImplementationDataTypes/uint16': '>u2',
        '/AUTOSAR_Platform/ImplementationDataTypes/uint32': '>u4',
        '/AUTOSAR_Platform/ImplementationDataTypes/uint64': '>u8',
        '/AUTOSAR_Platform/ImplementationDataTypes/sint8': '>i1',
        '/AUTOSAR_Platform/ImplementationDataTypes/sint16': '>i2',
        '/AUTOSAR_Platform/ImplementationDataTypes/sint32': '>i4',
        '/AUTOSAR_Platform/ImplementationDataTypes/sint64': '>i8',
        '/AUTOSAR_Platform/ImplementationDataTypes/float32': '>f4',
    }

    def __init__(
            self,
            version: str | float,
            patch: int | None,
            schema: str | None,
            release: int | None = None,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.major = 0
        self.minor = 0
        self.packages = []
        self.systems: list[System] = []
        if isinstance(version, str):
            major, minor, patch = parse_version_string(version)
            self._version = float(f'{major}.{minor}')
            self.patch = patch
        elif isinstance(version, float):
            self._version = version
            self.patch = patch
        self.release = None if release is None else release
        self.schema = schema
        self.package_parser: PackageParser | None = None
        self.xml_root: Element | None = None
        self.type_references = {}
        self.role_elements: dict[str, list] = {}
        self.map = {'packages': {}}
        self.profile = WorkspaceProfile()
        self.unhandled_parser = set()  # [PackageParser] Unhandled
        self.unhandled_writer = set()  # [PackageWriter] Unhandled

    @property
    def version(self) -> float:
        return self._version

    @version.setter
    def version(self, version: str | float):
        if isinstance(version, str):
            (major, minor, patch) = parse_version_string(version)
            self._version = float(f'{major}.{minor}')
            self.patch = patch
        elif isinstance(version, float):
            self._version = version

    def add_type_reference(self, name: str, type_ref: str):
        if type_ref not in self.autosar_platform_types:
            return
        self.type_references[name] = self.autosar_platform_types[type_ref]

    def open_xml(self, filename: Path):
        xml_root = parse_xml_file(filename)
        namespace = get_xml_namespace(xml_root)

        assert (namespace is not None)
        major, minor, patch, release, schema = parse_autosar_version_and_schema(xml_root)
        remove_namespace(xml_root, namespace)
        self.version = float(f'{major}.{minor}')
        self.major = major
        self.minor = minor
        self.patch = patch
        self.release = release
        self.schema = schema
        self.xml_root = xml_root
        if self.version < 3.0:
            raise NotImplementedError('Version below 3.0 is not supported')
        if self.package_parser is None:
            self.package_parser = PackageParser(self.version)
        self._register_default_element_parsers(self.package_parser)

    def load_xml(self, filename: Path):
        self.open_xml(filename)
        self.load_package('*')

    def load_package(self, package_name: str) -> list[Package]:
        found = False
        result = []
        if self.xml_root is None:
            raise ValueError('xmlroot is None, did you call loadXML() or openXML()?')
        if 3.0 <= self.version < 4.0:
            if self.xml_root.find('TOP-LEVEL-PACKAGES'):
                for xml_package in self.xml_root.findall('./TOP-LEVEL-PACKAGES/AR-PACKAGE'):
                    if self._load_package_internal(result, xml_package, package_name):
                        found = True

        elif self.version >= 4.0:
            if self.xml_root.find('AR-PACKAGES'):
                for xml_package in self.xml_root.findall('.AR-PACKAGES/AR-PACKAGE'):
                    if self._load_package_internal(result, xml_package, package_name):
                        found = True

        else:
            raise NotImplementedError(f'Version {self.version} of ARXML not supported')
        if not found and package_name != '*':
            raise KeyError(f'Package not found: {package_name}')

        if self.unhandled_parser:
            unhandled = ', '.join(self.unhandled_parser)
            self._logger.warning(f'Unhandled: {unhandled}')
        return result

    def _load_package_internal(self, result: list[Package], xml_package: Element, package_name: str) -> bool:
        name = xml_package.find("./SHORT-NAME").text
        found = False
        if package_name == '*' or package_name == name:
            found = True
            package = self.find(name)
            if package is None:
                package = Package(name, parent=self)
                self.packages.append(package)
                result.append(package)
                self.map['packages'][name] = package
            # self.package_parser.load_xml(package, xml_package)
            # self.unhandled_parser = self.unhandled_parser.union(package.unhandled_parser)
        return found

    def find(self, ref: str, role: str | None = None):
        if ref is None:
            return None

        if ref[0] == '/':
            ref = ref[1:]  # removes initial '/' if it exists
        ref = ref.partition('/')
        if ref[0] in self.map['packages']:
            pkg: Package = self.map['packages'][ref[0]]
            if len(ref[2]) > 0:
                return pkg.find(ref[2])
            return pkg
        return None

    def find_ws(self):
        return self

    def root_ws(self):
        return self

    @property
    def ref(self):
        return ''

    def _register_default_element_parsers(self, parser: PackageParser):
        parser.register_element_parser(DataTypeParser(self.version))
        parser.register_element_parser(DataTypeSemanticsParser(self.version))
        parser.register_element_parser(DataTypeUnitsParser(self.version))
        parser.register_element_parser(PortInterfacePackageParser(self.version))
        parser.register_element_parser(SoftwareAddressMethodParser(self.version))
        parser.register_element_parser(ModeDeclarationParser(self.version))
        parser.register_element_parser(ConstantParser(self.version))
        parser.register_element_parser(ComponentTypeParser(self.version))
        parser.register_element_parser(BehaviorParser(self.version))
        # parser.register_element_parser(SystemParser(self.version))
        # parser.register_element_parser(SignalParser(self.version))
        parser.register_element_parser(SwcImplementationParser(self.version))
        # parser.register_element_parser(ServiceInstanceCollectionParser(self.version))
        # parser.register_element_parser(CanClusterParser(self.version))
        # parser.register_element_parser(EthernetClusterParser(self.version))
        # parser.register_element_parser(TransformationParser(self.version))
        # parser.register_element_parser(PduParser(self.version))
        # parser.register_element_parser(SoConSetParser(self.version))
        # parser.register_element_parser(EcuParser(self.version))
        # parser.register_element_parser(CollectionParser(self.version))
        # parser.register_element_parser(SomeIpTpParser(self.version))
        # parser.register_element_parser(TransportProtocolParser(self.version))
        # parser.register_element_parser(FrameParser(self.version))


def get_xml_namespace(element: Element):
    m = re.match(r'\{(.*)}', element.tag)
    return m.group(1) if m else None


def remove_namespace(doc: Element, namespace: str):
    """Removes XML namespace in place."""
    namespace = f'{{{namespace}}}'
    for elem in doc.iter():
        elem.tag = elem.tag.removeprefix(namespace)


def parse_xml_file(filename: Path, namespace: str | None = None):
    arxml_tree = ElementTree()
    arxml_tree.parse(filename)
    arxml_root = arxml_tree.getroot()
    if namespace is not None:
        remove_namespace(arxml_root, namespace)
    return arxml_root
