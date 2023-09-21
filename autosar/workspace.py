from collections import UserDict, deque
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.base import (
    parse_xml_file,
    get_xml_namespace,
    remove_namespace,
    parse_autosar_version_and_schema,
    parse_version_string,
    create_admin_data,
)
from autosar.package import Package
from autosar.parser.behavior_parser import BehaviorParser
from autosar.parser.collection_parser import CollectionParser
from autosar.parser.component_parser import ComponentTypeParser
from autosar.parser.constant_parser import ConstantParser
from autosar.parser.data_transformation_parser import DataTransformationSetParser
from autosar.parser.datatype_parser import DataTypeParser, DataTypeSemanticsParser, DataTypeUnitsParser
from autosar.parser.ecu_parser import EcuParser
from autosar.parser.ethernet_cluster_parser import EthernetClusterParser
from autosar.parser.mode_parser import ModeDeclarationParser
from autosar.parser.package_parser import PackageParser
from autosar.parser.parser_base import ElementParser
from autosar.parser.pdu_parser import PduParser, SoConSetParser
from autosar.parser.portinterface_parser import PortInterfacePackageParser, SoftwareAddressMethodParser
from autosar.parser.service_instance_collection_parser import ServiceInstanceCollectionParser
from autosar.parser.signal_parser import SignalParser
from autosar.parser.some_ip_tp_parser import SomeIpTpParser
from autosar.parser.swc_implementation_parser import SwcImplementationParser
from autosar.parser.system_parser import SystemParser

_valid_ws_roles = [
    'DataType',
    'Constant',
    'PortInterface',
    'ComponentType',
    'ModeDclrGroup',
    'CompuMethod',
    'Unit',
    'BaseType',
    'DataConstraint',
]


class PackageRoles(UserDict):
    def __init__(self, data: Mapping | None = None):
        if data is None:
            data = {
                'DataType': None,
                'Constant': None,
                'PortInterface': None,
                'ModeDclrGroup': None,
                'ComponentType': None,
                'CompuMethod': None,
                'Unit': None,
                'DataConstraint': None,
            }
        super().__init__(data)


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
    An autosar worspace
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
            attributes: Any = None,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.major = 0
        self.minor = 0
        self.packages = []
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
        self.attributes = attributes
        self.type_references = {}
        self.role_elements = {}
        self.roles = PackageRoles()
        self.role_stack = deque()  # stack of PackageRoles
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

    @property
    def version_str(self) -> str:
        if self.patch is None:
            return str(self._version)
        else:
            return f'{self._version}.{self.patch}'

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.find(key)
        else:
            raise ValueError('expected string')

    @staticmethod
    def _adjust_file_ref(file_ref: dict[str, Path], base_dir: Path) -> Path:
        base_name = file_ref['path'].name
        dir_name = base_dir / file_ref['path'].parent
        retval = dir_name / base_name
        return retval

    def get_role(self, role: str):
        return self.roles[role]

    def set_role(self, ref: str, role: str):
        if (role is not None) and (role not in _valid_ws_roles):
            raise ValueError(f'Invalid role name: {role}')
        if ref is None:
            self.roles[role] = None
        else:
            package = self.find(ref)
            if package is None:
                raise ValueError(f'Invalid reference: {ref}')
            if not isinstance(package, Package):
                raise ValueError(f'Invalid type "{type(package)}" for reference "{ref}", expected Package type')
            package.role = role
            self.roles[role] = package.ref

    def set_roles(self, *items):
        """
        Same as setRole but caller gives a list of tuples where the first item is the package reference, and second item is the role name
        """
        for item in items:
            self.set_role(item[0], item[1])

    def push_roles(self):
        """
        Saves current package role settings in internal role stack
        """
        self.role_stack.append(PackageRoles(self.roles))

    def pop_roles(self):
        """
        Restores last saved package role settings
        """
        roles = self.role_stack.pop()
        self.roles.update(roles)

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

    def load_xml(self, filename: Path, roles: Mapping | None = None):
        global _valid_ws_roles
        self.open_xml(filename)
        self.load_package('*')
        if roles is not None:
            if not isinstance(roles, Mapping):
                raise ValueError('Roles parameter must be a dictionary or Mapping')
            for ref, role in roles.items():
                self.set_role(ref, role)

    def load_package(self, package_name: str, role: str | None = None) -> list[Package]:
        found = False
        result = []
        if self.xml_root is None:
            raise ValueError('xmlroot is None, did you call loadXML() or openXML()?')
        if 3.0 <= self.version < 4.0:
            if self.xml_root.find('TOP-LEVEL-PACKAGES'):
                for xml_package in self.xml_root.findall('./TOP-LEVEL-PACKAGES/AR-PACKAGE'):
                    if self._load_package_internal(result, xml_package, package_name, role):
                        found = True

        elif self.version >= 4.0:
            if self.xml_root.find('AR-PACKAGES'):
                for xml_package in self.xml_root.findall('.AR-PACKAGES/AR-PACKAGE'):
                    if self._load_package_internal(result, xml_package, package_name, role):
                        found = True

        else:
            raise NotImplementedError(f'Version {self.version} of ARXML not supported')
        if not found and package_name != '*':
            raise KeyError(f'Package not found: {package_name}')

        if self.unhandled_parser:
            unhandled = ', '.join(self.unhandled_parser)
            self._logger.warning(f'Unhandled: {unhandled}')
        return result

    def _load_package_internal(self, result: list[Package], xml_package: Element, package_name: str, role: str) -> bool:
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
            self.package_parser.load_xml(package, xml_package)
            self.unhandled_parser = self.unhandled_parser.union(package.unhandled_parser)
            if (package_name == name) and (role is not None):
                self.set_role(package.ref, role)
        return found

    def find(self, ref: str, role: str | None = None):
        global _valid_ws_roles
        if ref is None:
            return None
        if (role is not None) and (ref[0] != '/'):
            if role not in _valid_ws_roles:
                raise ValueError(f'Unknown role name: {role}')
            if self.roles[role] is not None:
                ref = f'{self.roles[role]}/{ref}'  # appends the role packet name in front of ref

        if ref[0] == '/':
            ref = ref[1:]  # removes initial '/' if it exists
        ref = ref.partition('/')
        if ref[0] in self.map['packages']:
            pkg: Package = self.map['packages'][ref[0]]
            if len(ref[2]) > 0:
                return pkg.find(ref[2])
            return pkg
        return None

    def findall(self, ref: str):
        """
        experimental find-method that has some rudimentary support for globs.
        """
        if ref is None:
            return None
        if ref[0] == '/':
            ref = ref[1:]  # removes initial '/' if it exists
        ref = ref.partition('/')
        if ref[0] == '*' and len(ref[2]) == 0:
            result = list(self.packages)
        else:
            result = []
            for pkg in self.packages:
                if pkg.name == ref[0] or ref[0] == '*':
                    if len(ref[2]) > 0:
                        result.extend(pkg.findall(ref[2]))
                    else:
                        result.append(pkg)
        return result

    def find_role_package(self, role_name: str):
        """
        Returns package with role set to roleName or None
        """
        if role_name is None:
            return None
        for pkg in self.packages:
            if pkg.role == role_name:
                return pkg
            elif len(pkg.sub_packages) > 0:
                for child_pkg in pkg.sub_packages:
                    if child_pkg.role == role_name:
                        return child_pkg
        return None

    def create_package(self, name: str, role: str | None = None):
        if name not in self.map['packages']:
            package = Package(name, self)
            self.packages.append(package)
            self.map['packages'][name] = package
            if role is not None:
                self.set_role(package.ref, role)
            return package
        else:
            return self.map['packages'][name]

    def dir(self, ref: str | None = None, _prefix: str = '/'):
        if ref is None:
            return [x.name for x in self.packages]
        else:
            if ref[0] == '/':
                ref = ref[1:]
            ref = ref.partition('/')
            result = self.find(ref[0])
            if result is not None:
                return result.dir(ref[2] if len(ref[2]) > 0 else None, _prefix + ref[0] + '/')
            else:
                return None

    def find_ws(self):
        return self

    def root_ws(self):
        return self

    def append(self, elem: Package):
        if isinstance(elem, Package):
            self.packages.append(elem)
            elem.parent = self
            self.map['packages'][elem.name] = elem
        else:
            raise ValueError(type(elem))

    @property
    def ref(self):
        return ''

    def list_packages(self):
        """returns a list of strings containig the package names of the opened XML file"""
        package_list = []
        if self.xml_root is None:
            raise ValueError('xmlroot is None, did you call loadXML() or openXML()?')
        if 3.0 <= self.version < 4.0:
            if self.xml_root.find('TOP-LEVEL-PACKAGES'):
                for xml_package in self.xml_root.findall('./TOP-LEVEL-PACKAGES/AR-PACKAGE'):
                    package_list.append(xml_package.find('./SHORT-NAME').text)
        elif self.version >= 4.0:
            if self.xml_root.find('AR-PACKAGES'):
                for xml_package in self.xml_root.findall('.AR-PACKAGES/AR-PACKAGE'):
                    package_list.append(xml_package.find('./SHORT-NAME').text)
        else:
            raise NotImplementedError(f'Version {self.version} of ARXML not supported')
        return package_list

    def delete(self, ref: str):
        if ref is None:
            return
        if ref[0] == '/':
            ref = ref[1:]  # removes initial '/' if it exists
        ref = ref.partition('/')
        for i, pkg in enumerate(self.packages):
            if pkg.name == ref[0]:
                if len(ref[2]) > 0:
                    return pkg.delete(ref[2])
                else:
                    del self.packages[i]
                    del self.map['packages'][ref[0]]
                    break

    @staticmethod
    def create_admin_data(data: dict[str, Any]):
        return create_admin_data(data)

    def apply(self, template, **kwargs):
        """
        Applies template to this workspace
        """
        if len(kwargs) == 0:
            template.apply(self)
        else:
            template.apply(self, **kwargs)
        template.usage_count += 1

    def register_element_parser(self, element_parser: ElementParser):
        """
        Registers a custom element parser object
        """
        if self.package_parser is None:
            self.package_parser = PackageParser(self.version)
            self._register_default_element_parsers(self.package_parser)
        self.package_parser.register_element_parser(element_parser)

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
        parser.register_element_parser(SystemParser(self.version))
        parser.register_element_parser(SignalParser(self.version))
        parser.register_element_parser(SwcImplementationParser(self.version))
        parser.register_element_parser(ServiceInstanceCollectionParser(self.version))
        parser.register_element_parser(EthernetClusterParser(self.version))
        parser.register_element_parser(DataTransformationSetParser(self.version))
        parser.register_element_parser(PduParser(self.version))
        parser.register_element_parser(SoConSetParser(self.version))
        parser.register_element_parser(EcuParser(self.version))
        parser.register_element_parser(CollectionParser(self.version))
        parser.register_element_parser(SomeIpTpParser(self.version))
