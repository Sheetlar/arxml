import copy
import decimal
import re
from fractions import Fraction
from typing import Iterable, Mapping, Sequence

from autosar.ar_object import ArObject
from autosar.base import (
    create_admin_data,
    index_by_name,
    AdminData,
    SwDataDefPropsConditional,
    SwPointerTargetProps,
    InvalidDataTypeRef,
    InvalidDataConstraintRef,
    InvalidCompuMethodRef,
)
from autosar.behavior import InternalBehavior, SwcInternalBehavior
from autosar.builder import ValueBuilder
from autosar.element import Element, ParameterDataPrototype, SoftwareAddressMethod
from autosar.mode import ModeGroup, ModeDeclaration, ModeDeclarationGroup
from autosar.component import (
    AtomicSoftwareComponent,
    ApplicationSoftwareComponent,
    ComplexDeviceDriverComponent,
    CompositionComponent,
    NvBlockComponent,
    ServiceComponent,
    SwcImplementation,
)
from autosar.constant import (
    Constant,
    ValueAR4,
    IntegerValue,
    BooleanValue,
    NumericalValue,
    StringValue,
    TextValue,
    ArrayValue,
    RecordValue,
    ApplicationValue, SwAxisCont, SwValueCont,
)
from autosar.datatype import (
    IntegerDataType,
    RealDataType,
    BooleanDataType,
    StringDataType,
    ArrayDataType,
    RecordDataType,
    SwBaseType,
    ApplicationPrimitiveDataType,
    ApplicationArrayDataType,
    ApplicationRecordDataType,
    ImplementationDataType,
    RecordTypeElement,
    ImplementationDataTypeElement,
    DataTypeMappingSet,
    DataConstraint,
    Computation,
    CompuMethod,
    Unit, DataType, ApplicationDataType, ApplicationArrayElement,
)
from autosar.portinterface import (
    Operation,
    DataElement,
    SenderReceiverInterface,
    ClientServerInterface,
    ModeSwitchInterface,
    ParameterInterface,
    NvDataInterface,
    ApplicationError,
)


class Package(ArObject):
    package_name = None

    def __init__(self, name: str, parent: ArObject | None = None, role: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.elements: list[Element] = []
        self.sub_packages: list[Package] = []
        self.parent = parent
        self.role = role
        self.map = {'elements': {}, 'packages': {}}
        self.unhandled_parser = set()  # [PackageParser] unhandled
        self.unhandled_writer = set()  # [PackageWriter] Unhandled

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.find(key)
        else:
            raise ValueError('Expected string')

    @property
    def ref(self):
        if self.parent is not None:
            return f'{self.parent.ref}/{self.name}'
        else:
            return None

    def find(self, ref: str):
        if ref.startswith('/'):
            return self.parent.find(ref)
        ref = ref.partition('/')
        name = ref[0]
        if name in self.map['packages']:
            package: Package = self.map['packages'][name]
            if len(ref[2]) > 0:
                return package.find(ref[2])
            else:
                return package
        if name in self.map['elements']:
            elem: Element = self.map['elements'][name]
            if len(ref[2]) > 0:
                return elem.find(ref[2])
            else:
                return elem
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
            result = list(self.elements)
            result.extend(self.sub_packages)
        else:
            result = []
            for item in (self.elements + self.sub_packages):
                if item.name == ref[0] or ref[0] == '*':
                    if len(ref[2]) > 0:
                        result.extend(item.findall(ref[2]))
                    else:
                        result.append(item)
            if (len(result) == 0) and ('*' in ref[0]):
                p = re.compile(ref[0].replace('*', '.*'))
                for item in (self.elements + self.sub_packages):
                    m = p.match(item.name)
                    if m is not None:
                        if len(ref[2]) > 0:
                            result.extend(item.findall(ref[2]))
                        else:
                            result.append(item)
        return result

    def dir(self, ref: str | None = None, prefix: str = ''):
        if ref is None:
            return [prefix + x.name for x in self.sub_packages] + [prefix + x.name for x in self.elements]
        else:
            ref = ref.partition('/')
            result = self.find(ref[0])
            if result is not None:
                return result.dir(ref[2] if len(ref[2]) > 0 else None, prefix + ref[0] + '/')
            else:
                return None

    def delete(self, ref: str):
        if ref is None:
            return
        if ref[0] == '/':
            ref = ref[1:]  # removes initial '/' if it exists
        ref = ref.partition('/')
        for i, element in enumerate(self.elements):
            if element.name == ref[0]:
                if len(ref[2]) > 0:
                    return element.delete(ref[2])
                else:
                    del self.elements[i]
                    del self.map['elements'][ref[0]]
                    break

    def create_sender_receiver_interface(
            self,
            name: str,
            data_elements: DataElement | Iterable[DataElement] | None = None,
            mode_groups: ModeGroup | Iterable[ModeGroup] | None = None,
            is_service: bool = False,
            admin_data: AdminData | None = None,
    ):
        """
        creates a new sender-receiver port interface. dataElements can either be a single instance of DataElement or a list of DataElements.
        The same applies to modeGroups. isService must be boolean
        """

        ws = self.root_ws()
        assert (ws is not None)

        port_interface = SenderReceiverInterface(name, is_service, admin_data=admin_data)
        if data_elements is not None:
            if isinstance(data_elements, Iterable):
                for elem in data_elements:
                    data_type = ws.find(elem.type_ref, role='DataType')
                    if data_type is None:
                        raise ValueError(f'Invalid type reference: {elem.type_ref}')
                    elem.type_ref = data_type.ref  # normalize reference to data element
                    port_interface.append(elem)
            elif isinstance(data_elements, DataElement):
                data_type = ws.find(data_elements.type_ref, role='DataType')
                if data_type is None:
                    raise ValueError(f'Invalid type reference: {data_elements.type_ref}')
                data_elements.type_ref = data_type.ref  # normalize reference to data element
                port_interface.append(data_elements)
            else:
                raise ValueError('dataElements: expected autosar.portinterface.DataElement instance or list')
        if mode_groups is not None:
            if isinstance(mode_groups, Iterable):
                for elem in mode_groups:
                    port_interface.append(elem)
            elif isinstance(mode_groups, ModeGroup):
                port_interface.append(mode_groups)
            else:
                raise ValueError('dataElements: expected autosar.portinterface.DataElement instance or list')
        self.append(port_interface)
        return port_interface

    def create_parameter_interface(
            self,
            name: str,
            parameters: DataElement | ParameterDataPrototype | Iterable[DataElement | ParameterDataPrototype] | None = None,
            admin_data: AdminData | None = None,
    ):
        """
        Creates a new parameter port interface. parameter can either be a single instance of Parameter or a list of Parameters.
        The same applies to modeDeclarationGroups. isService must be boolean.
        In a previous version of this function the class DataElement was used instead of Parameter.
        In order to be backward compatible with old code, this method converts from old to new datatype internally
        """
        ws = self.root_ws()
        assert (ws is not None)

        if isinstance(admin_data, dict):
            admin_data_obj = ws.createAdminData(admin_data)
        else:
            admin_data_obj = admin_data
        if (admin_data_obj is not None) and not isinstance(admin_data_obj, AdminData):
            raise ValueError('adminData must be of type dict or AdminData')
        port_interface = ParameterInterface(name, admin_data=admin_data_obj)
        if parameters is not None:
            if isinstance(parameters, Iterable):
                for elem in parameters:
                    data_type = ws.find(elem.type_ref, role='DataType')
                    # normalize reference to data element
                    if data_type is None:
                        raise ValueError(f'Invalid type reference: {elem.type_ref}')
                    elem.type_ref = data_type.ref
                    if isinstance(elem, DataElement):
                        # convert into Parameter
                        parameter = ParameterDataPrototype(elem.name, elem.type_ref, elem.sw_address_method_ref, admin_data=elem.admin_data)
                    else:
                        parameter = elem
                    port_interface.append(parameter)
            elif isinstance(parameters, DataElement):
                data_type = ws.find(parameters.type_ref, role='DataType')
                # normalize reference to data element
                if data_type is None:
                    raise ValueError(f'Invalid type reference: {parameters.type_ref}')
                parameters.type_ref = data_type.ref
                parameter = ParameterDataPrototype(
                    parameters.name,
                    parameters.type_ref,
                    parameters.sw_address_method_ref,
                    admin_data=parameters.admin_data,
                )
                port_interface.append(parameter)
            elif isinstance(parameters, ParameterDataPrototype):
                data_type = ws.find(parameters.type_ref, role='DataType')
                # normalize reference to data element
                if data_type is None:
                    raise ValueError(f'Invalid type reference: {parameters.type_ref}')
                parameters.type_ref = data_type.ref
                port_interface.append(parameters)
            else:
                raise ValueError('parameters: Expected instance of autosar.element.ParameterDataPrototype or list')
        self.append(port_interface)
        return port_interface

    def create_mode_switch_interface(
            self,
            name: str,
            mode_group: ModeGroup | None = None,
            is_service: bool = False,
            admin_data: AdminData | None = None,
    ):
        port_interface = ModeSwitchInterface(name, is_service, self, admin_data)
        if mode_group is not None:
            if isinstance(mode_group, ModeGroup):
                ws = self.root_ws()
                assert (ws is not None)
                mode_declaration_group = ws.find(mode_group.type_ref, role='ModeDclrGroup')
                if mode_declaration_group is None:
                    raise ValueError(f'Invalid type reference: {mode_group.type_ref}')
                mode_group.type_ref = mode_declaration_group.ref  # normalize reference string
                port_interface.mode_group = mode_group
                mode_group.parent = port_interface
            else:
                raise ValueError('modeGroup must be an instance of autosar.mode.ModeGroup or None')
        self.append(port_interface)
        return port_interface

    def create_nv_data_interface(
            self,
            name: str,
            nv_data: DataElement | Iterable[DataElement] | None = None,
            is_service: bool = False,
            service_kind: str | None = None,
            admin_data: AdminData | None = None,
    ):
        """
        creates a new nv-data port interface. nv_data can either be a single instance of DataElement or a list of DataElements.
        isService must be boolean
        """

        ws = self.root_ws()
        assert (ws is not None)

        port_interface = NvDataInterface(str(name), is_service=is_service, service_kind=service_kind, admin_data=admin_data)
        if nv_data is not None:
            if isinstance(nv_data, Iterable):
                for elem in nv_data:
                    data_type = ws.find(elem.type_ref, role='DataType')
                    if data_type is None:
                        raise ValueError(f'Invalid type reference: {elem.type_ref}')
                    elem.type_ref = data_type.ref  # normalize reference to data element
                    port_interface.append(elem)
            elif isinstance(nv_data, DataElement):
                data_type = ws.find(nv_data.type_ref, role='DataType')
                if data_type is None:
                    raise ValueError(f'Invalid type reference: {nv_data.type_ref}')
                nv_data.type_ref = data_type.ref  # normalize reference to data element
                port_interface.append(nv_data)
            else:
                raise ValueError('dataElements: expected autosar.portinterface.DataElement instance or list')
        self.append(port_interface)
        return port_interface

    def create_sub_package(self, name: str, role: str | None = None):
        pkg = Package(name)
        self.append(pkg)
        if role is not None:
            ws = self.root_ws()
            assert (ws is not None)
            ws.setRole(pkg.ref, role)
        return pkg

    def root_ws(self):
        if self.parent is None:
            return None
        else:
            return self.parent.root_ws()

    def append(self, elem: 'Element | Package'):
        """appends elem to the self.elements list"""
        is_new_element = True
        if elem.name in self.map['elements']:
            is_new_element = False
            existing_elem = self.map['elements'][elem.name]
            if type(elem) != type(existing_elem):
                raise TypeError(f'Error: element {type(existing_elem)} {existing_elem.name} already exists in package {self.name} '
                                f'with different type from new element {type(elem)}')
            else:
                if elem != existing_elem:
                    raise ValueError(f'Error: element {existing_elem.name} {type(existing_elem)} already exist in package {self.name} '
                                     f'using different definition')
        if is_new_element:
            if isinstance(elem, Element):
                self.elements.append(elem)
                elem.parent = self
                self.map['elements'][elem.name] = elem
            elif isinstance(elem, Package):
                self.sub_packages.append(elem)
                elem.parent = self
                self.map['packages'][elem.name] = elem
            else:
                raise ValueError(f'Unexpected value type {type(elem)}')

    def update(self, other: 'Package'):
        """copies/clones each element from other into self.elements"""
        if type(self) == type(other):
            for other_elem in other.elements:
                new_elem = copy.deepcopy(other_elem)
                assert (new_elem is not None)
                try:
                    i = self.index('elements', other_elem.name)
                    old_elem = self.elements[i]
                    self.elements[i] = new_elem
                    old_elem.parent = None
                except ValueError:
                    self.elements.append(new_elem)
                new_elem.parent = self
        else:
            raise ValueError('Cannot update from object of different type')

    def index(self, container: str, name: str):
        if container == 'elements':
            lst = self.elements
        elif container == 'subPackages':
            lst = self.sub_packages
        else:
            raise KeyError(f'{container} not in {self.__class__.__name__}')
        return index_by_name(lst, name)

    def create_application_software_component(
            self,
            swc_name: str,
            behavior_name: str | None = None,
            implementation_name: str | None = None,
            multiple_instance: bool = False,
            auto_create_port_api_options: bool = True,
    ):
        """
        Creates a new ApplicationSoftwareComponent object and adds it to the package.
        It also creates an InternalBehavior object as well as an SwcImplementation object.

        """
        ws = self.root_ws()
        assert (ws is not None)
        swc = ApplicationSoftwareComponent(swc_name, self)
        self.append(swc)
        self._create_internal_behavior(ws, swc, behavior_name, multiple_instance, auto_create_port_api_options)
        self._create_implementation(swc, implementation_name)
        return swc

    def create_service_component(
            self,
            swc_name: str,
            behavior_name: str | None = None,
            implementation_name: str | None = None,
            multiple_instance: bool = False,
            auto_create_port_api_options: bool = True,
    ):
        """
        Creates a new ApplicationSoftwareComponent object and adds it to the package.
        It also creates an InternalBehavior object as well as an SwcImplementation object.
        """
        ws = self.root_ws()
        assert (ws is not None)

        swc = ServiceComponent(swc_name, self)
        self.append(swc)
        self._create_internal_behavior(ws, swc, behavior_name, multiple_instance, auto_create_port_api_options)
        self._create_implementation(swc, implementation_name)
        return swc

    def create_complex_device_driver_component(
            self,
            swc_name: str,
            behavior_name: str | None = None,
            implementation_name: str | None = None,
            multiple_instance: bool = False,
            auto_create_port_api_options: bool = True,
    ):
        ws = self.root_ws()
        assert (ws is not None)
        swc = ComplexDeviceDriverComponent(swc_name, parent=self)
        self.append(swc)
        self._create_internal_behavior(ws, swc, behavior_name, multiple_instance, auto_create_port_api_options)
        self._create_implementation(swc, implementation_name)
        return swc

    def create_nv_block_component(
            self,
            swc_name: str,
            behavior_name: str | None = None,
            implementation_name: str | None = None,
            multiple_instance: bool = False,
            auto_create_port_api_options: bool = False,
    ):
        """
        Creates a new NvBlockComponent object and adds it to the package.
        It also creates an InternalBehavior object as well as an SwcImplementation object.

        """
        ws = self.root_ws()
        assert (ws is not None)
        swc = NvBlockComponent(swc_name, self)
        self.append(swc)
        self._create_internal_behavior(ws, swc, behavior_name, multiple_instance, auto_create_port_api_options)
        self._create_implementation(swc, implementation_name)
        return swc

    def create_composition_component(self, component_name: str):
        component = CompositionComponent(component_name, self)
        self.append(component)
        return component

    def _create_internal_behavior(
            self,
            ws,
            swc: AtomicSoftwareComponent,
            behavior_name: str | None,
            multiple_instance: bool,
            auto_create_port_api_options: bool,
    ):
        """
        Initializes swc.behavior object
        For AUTOSAR3, an instance of InternalBehavior is created
        For AUTOSAR4, an instance of SwcInternalBehavior is created
        """
        if behavior_name is None:
            behavior_name = f'{swc.name}_InternalBehavior'
        if ws.version < 4.0:
            # In AUTOSAR 3.x the internal behavior is a sub-element of the package.
            internal_behavior = InternalBehavior(behavior_name, swc.ref, multiple_instance, self)
        else:
            # In AUTOSAR 4.x the internal behavior is a sub-element of the swc.
            internal_behavior = SwcInternalBehavior(behavior_name, swc.ref, multiple_instance, swc)
        internal_behavior.auto_create_port_api_options = auto_create_port_api_options
        swc.behavior = internal_behavior
        if ws.version < 4.0:
            # In AUTOSAR 3.x the internal behavior is a sub-element of the package.
            self.append(internal_behavior)

    def _create_implementation(self, swc: AtomicSoftwareComponent, implementation_name: str):

        if implementation_name is None:
            implementation_name = f'{swc.name}_Implementation'
        swc.implementation = SwcImplementation(implementation_name, swc.behavior.ref, parent=self)

        self.append(swc.implementation)

    def create_mode_declaration_group(
            self,
            name: str,
            mode_declarations: Iterable[str | tuple] | None = None,
            initial_mode: str | None = None,
            category: str | None = None,
            admin_data: AdminData | None = None,
    ):
        """
        creates an instance of autosar.portinterface.ModeDeclarationGroup
        name: name of the ModeDeclarationGroup
        modeDeclarations: list of strings where each string is a mode name. It can also be a list of tuples of type (int, str).
        initialMode: string with name of the initial mode (must be one of the strings in modeDeclarations list)
        category: optional category string
        adminData: optional adminData object (use ws.createAdminData() as constructor)
        """
        ws = self.root_ws()
        assert (ws is not None)
        if isinstance(admin_data, dict):
            admin_data_obj = ws.createAdminData(admin_data)
        else:
            admin_data_obj = admin_data
        if (admin_data_obj is not None) and not isinstance(admin_data_obj, AdminData):
            raise ValueError("adminData must be of type dict or AdminData")
        group = ModeDeclarationGroup(name, None, None, category, self, admin_data_obj)
        if mode_declarations is not None:
            for declaration in mode_declarations:
                if isinstance(declaration, str):
                    declaration_name = declaration
                    item = ModeDeclaration(declaration_name, parent=group)
                elif isinstance(declaration, tuple):
                    declaration_value = declaration[0]
                    declaration_name = declaration[1]
                    assert (isinstance(declaration_value, int))
                    assert (isinstance(declaration_name, str))
                    item = ModeDeclaration(declaration_name, declaration_value, group)
                else:
                    raise NotImplementedError(type(declaration))
                group.mode_declarations.append(item)
                if (initial_mode is not None) and (declaration_name == initial_mode):
                    group.initial_mode_ref = item.ref
            if (initial_mode is not None) and (group.initial_mode_ref is None):
                raise ValueError(f'initalMode "{initial_mode}" not a valid modeDeclaration name')
            self.append(group)
        return group

    def create_client_server_interface(
            self,
            name: str,
            operations: Iterable[str],
            errors: ApplicationError | Iterable[ApplicationError] | None = None,
            is_service: bool = False,
            service_kind: str | None = None,
            admin_data: AdminData | None = None,
    ):
        """
        creates a new client server interface in current package
        name: name of the interface (string)
        operations: names of the operations in the interface (list of strings)
        errors: Possible errors that can be returned. Can be a single instance of ApplicationError or a list of ApplicationError
        isService: True if this interface is a service interface (bool)
        adminData: optional admindata (dict or autosar.base.AdminData object)
        """
        port_interface = ClientServerInterface(name, is_service, service_kind, self, admin_data)
        for name in operations:
            port_interface.append(Operation(name))
        if errors is not None:
            if isinstance(errors, Iterable):
                for error in errors:
                    port_interface.append(error)
            else:
                assert (isinstance(errors, ApplicationError))
                port_interface.append(errors)
        self.append(port_interface)
        return port_interface

    def create_software_address_method(self, name: str):
        item = SoftwareAddressMethod(name)
        self.append(item)
        return item

    def create_array_data_type(
            self,
            name: str,
            type_ref: str,
            array_size: int,
            admin_data: AdminData | None = None,
    ):
        """
        AUTOSAR3:
           Creates an ArrayDataType and adds it to current package
        """
        ws = self.root_ws()
        assert (ws is not None)
        if ws.version >= 4.0:
            raise RuntimeError("This method is only valid in AUTOSAR3")
        else:
            if type_ref.startswith('/'):
                data_type = ws.find(type_ref)
            else:
                data_type = ws.find(type_ref, role='DataType')
            if data_type is None:
                raise InvalidDataTypeRef(type_ref)
            new_type = ArrayDataType(name, type_ref, array_size, admin_data)
            self.append(new_type)
            return new_type

    def create_integer_data_type(
            self,
            name: str,
            min_value: int | None = None,
            max_value: int | None = None,
            value_table: Iterable[str | tuple] | None = None,
            offset: int | float | None = None,
            scaling: int | float | None = None,
            unit: str | None = None,
            admin_data: AdminData | None = None,
            force_float_scaling: bool = False,
    ):
        """
        AUTOSAR3:
        Helper method for creating integer datatypes in a package.
        In order to use this function you must have a subpackage present with role='CompuMethod'.

        AUTOSAR4:
        Helper method for creating implementation datatypes or application datatypes.
        """
        ws = self.root_ws()
        assert (ws is not None)
        if ws.version >= 4.0:
            raise RuntimeError("This method is only valid in AUTOSAR3")
        else:
            compu_method_ref = self._create_compu_method_and_unit_v3(
                ws,
                name,
                min_value,
                max_value,
                value_table,
                None,
                offset,
                scaling,
                unit,
                force_float_scaling,
            )
            lower_limit, upper_limit = min_value, max_value
            if compu_method_ref is not None:
                compu_method = ws.find(compu_method_ref)
                if lower_limit is None:
                    lower_limit = compu_method.int_to_phys.lower_limit
                if upper_limit is None:
                    upper_limit = compu_method.int_to_phys.upper_limit
            new_type = IntegerDataType(name, lower_limit, upper_limit, compu_method_ref=compu_method_ref, admin_data=admin_data)
            assert (new_type is not None)
            self.append(new_type)
            return new_type

    def create_real_data_type(
            self,
            name: str,
            min_val: float | str,
            max_val: float | str,
            min_val_type: str = 'CLOSED',
            max_val_type: str = 'CLOSED',
            has_nan: bool = False,
            encoding: str = 'SINGLE',
            base_type_ref: str | None = None,
            type_emitter: str | None = None,
            admin_data: AdminData | None = None,
    ):
        """
        AUTOSAR 4: Creates a new ImplementationDataType
        AUTOSAR 3: Creates a new instance of autosar.datatype.RealDataType and appends it to current package
        """
        ws = self.root_ws()
        assert (ws is not None)
        if ws.version >= 4.0:
            if base_type_ref is None:
                raise ValueError('baseTypeRef argument must be given to this method')
            if min_val == '-INFINITE' or min_val == 'INFINITE':
                min_val = '-INF'
            if max_val == 'INFINITE':
                max_val = 'INF'
            if min_val == '-INF' and min_val_type == 'CLOSED':
                min_val_type = 'OPEN'  # automatic correction
            if max_val == 'INF' and max_val_type == 'CLOSED':
                max_val_type = 'OPEN'  # automatic correction
            data_constraint = self.create_internal_data_constraint(f'{name}_DataConstr', min_val, max_val, min_val_type, max_val_type)
            new_type = ImplementationDataType(name, category='VALUE', type_emitter=type_emitter)
            props = SwDataDefPropsConditional(
                base_type_ref=base_type_ref,
                sw_calibration_access='NOT-ACCESSIBLE',
                data_constraint_ref=data_constraint.ref,
            )
            new_type.variant_props = [props]
        else:
            if (min_val == '-INFINITE') or (min_val == '-INF') or (min_val == 'INFINITE') or (min_val == 'INF'):
                # automatic correction
                min_val = None
                min_val_type = 'INFINITE'
            if (max_val == 'INF') or (max_val == 'INFINITE'):
                # automatic correction
                max_val = None
                max_val_type = 'INFINITE'
            new_type = RealDataType(name, min_val, max_val, min_val_type, max_val_type, has_nan, encoding, self, admin_data)
        self.append(new_type)
        return new_type

    def create_record_data_type(self, name: str, elements: Iterable, admin_data: AdminData | None = None):
        """
        AUTOSAR3: Create a new instance of RecordDataType and appends it to current package
        """
        ws = self.root_ws()
        assert (ws is not None)
        if ws.version >= 4.0:
            raise RuntimeError("This method is only for AUTOSAR3")
        processed = []
        for elem in elements:
            if isinstance(elem, RecordTypeElement):
                processed.append(elem)
            else:
                if isinstance(elem, tuple):
                    elem_name, elem_unit_ref = elem
                elif isinstance(elem, Mapping):
                    elem_name = elem['name']
                    elem_unit_ref = elem['typeRef']
                else:
                    raise ValueError('Element must be either Mapping, RecordTypeElement or tuple')
                if elem_unit_ref.startswith('/'):
                    data_type = ws.find(elem_unit_ref)
                else:
                    data_type = ws.find(elem_unit_ref, role='DataType')
                if data_type is None:
                    raise InvalidDataTypeRef(elem_unit_ref)
                elem = RecordTypeElement(elem_name, data_type.ref)
                processed.append(elem)
            data_type = RecordDataType(name, processed, self, admin_data)
            self.append(data_type)
            return data_type

    def create_string_data_type(self, name: str, length: int, encoding: str = 'ISO-8859-1', admin_data: AdminData | None = None):
        """
        create a new instance of autosar.datatype.StringDataType and appends it to current package
        """
        data_type = StringDataType(name, length, encoding, self, admin_data)
        self.append(data_type)
        return data_type

    def create_boolean_data_type(self, name: str, admin_data: AdminData | None = None):
        """
        create a new instance of autosar.datatype.BooleanDataType and appends it to current package
        """
        data_type = BooleanDataType(name, self, admin_data)
        self.append(data_type)
        return data_type

    def create_constant(
            self,
            name: str,
            type_ref: str,
            init_value: str | int | float | bool | Iterable | Mapping,
            label: str = '',
            admin_data: AdminData | None = None,
    ):
        """
        create a new instance of autosar.constant.Constant and appends it to the current package
        """
        ws = self.root_ws()
        assert (ws is not None)
        if type_ref is not None:
            data_type = ws.find(type_ref, role='DataType')
            if data_type is None:
                raise InvalidDataTypeRef(str(type_ref))
        else:
            if ws.version < 4.0:
                raise ValueError('typeRef argument cannot be None')
            else:
                data_type = None
        if ws.version < 4.0:
            return self._create_constant_v3(ws, name, data_type, init_value, admin_data)
        else:
            return self._create_constant_v4(ws, name, data_type, init_value, label, admin_data)

    def _create_constant_v3(
            self,
            ws,
            name: str,
            data_type: DataType,
            init_value: str | int | float | bool | Iterable | Mapping,
            admin_data: AdminData | None = None,
    ):
        """Creates an AUTOSAR 3 Constant"""
        if isinstance(data_type, IntegerDataType):
            if not isinstance(init_value, int):
                raise ValueError(f'initValue: expected type int, got {type(init_value)}')
            value = IntegerValue(name, data_type.ref, init_value)
        elif isinstance(data_type, RecordDataType):
            if isinstance(init_value, Mapping) or isinstance(init_value, Iterable):
                pass
            else:
                raise ValueError(f'initValue: expected type Mapping or Iterable, got {type(init_value)}')
            value = self._create_record_value_v3(ws, name, data_type, init_value)
        elif isinstance(data_type, ArrayDataType):
            if isinstance(init_value, Iterable):
                pass
            else:
                raise ValueError(f'initValue: expected type Iterable, got {type(init_value)}')
            value = self._create_array_value_v3(ws, name, data_type, init_value)
        elif isinstance(data_type, BooleanDataType):
            if isinstance(init_value, bool):
                pass
            elif isinstance(init_value, str) or isinstance(init_value, int):
                init_value = bool(init_value)
            else:
                raise ValueError(f'initValue: expected type bool or str, got {type(init_value)}')
            value = BooleanValue(name, data_type.ref, init_value)
        elif isinstance(data_type, StringDataType):
            if isinstance(init_value, str):
                pass
            else:
                raise ValueError(f'initValue: expected type str, got {type(init_value)}')
            value = StringValue(name, data_type.ref, init_value)
        elif isinstance(data_type, RealDataType):
            if isinstance(init_value, float) or isinstance(init_value, decimal.Decimal) or isinstance(init_value, int):
                pass
            else:
                raise ValueError(f'initValue: expected type int, float or Decimal, got {type(init_value)}')
            raise NotImplementedError('Creating constants from RealDataType not implemented')
        else:
            raise ValueError(f'unrecognized type: {type(init_value)}')
        assert (value is not None)
        constant = Constant(name, value, admin_data=admin_data)
        self.append(constant)
        return constant

    def _create_record_value_v3(
            self,
            ws,
            name: str,
            data_type: RecordDataType,
            init_value: Mapping | Iterable,
            parent: ArObject | None = None,
    ):
        value = RecordValue(name, data_type.ref, parent=parent)
        if not isinstance(init_value, Mapping):
            raise NotImplementedError(type(init_value))
        for elem in data_type.elements:
            if elem.name in init_value:
                v = init_value[elem.name]
                child_type = ws.find(elem.type_ref)
                if child_type is None:
                    raise ValueError(f'Invalid reference: {elem.type_ref}')
                if isinstance(child_type, IntegerDataType):
                    if not isinstance(v, int):
                        raise ValueError(f'v: expected type int, got {type(v)}')
                    value.elements.append(IntegerValue(elem.name, child_type.ref, v, value))
                elif isinstance(child_type, RecordDataType):
                    if not isinstance(v, Mapping) and not isinstance(v, Iterable):
                        raise ValueError(f'v: expected type Mapping or Iterable, got {type(v)}')
                    value.elements.append(self._create_record_value_v3(ws, elem.name, child_type, v, value))
                elif isinstance(child_type, ArrayDataType):
                    if not isinstance(v, Iterable):
                        raise ValueError(f'v: expected type Iterable, got {type(v)}')
                    value.elements.append(self._create_array_value_v3(ws, elem.name, child_type, v, value))
                elif isinstance(child_type, BooleanDataType):
                    if not isinstance(v, str) and not isinstance(v, int):
                        raise ValueError(f'v: expected type bool or str, got {type(v)}')
                    v = bool(v)
                    value.elements.append(BooleanValue(elem.name, child_type.ref, v, value))
                elif isinstance(child_type, StringDataType):
                    if not isinstance(v, str):
                        raise ValueError(f'v: expected type str, got {type(v)}')
                    value.elements.append(StringValue(elem.name, child_type.ref, v, value))
                elif isinstance(child_type, RealDataType):
                    if not isinstance(v, float) and not isinstance(v, decimal.Decimal) and not isinstance(v, int):
                        raise ValueError(f'v: expected type int, float or Decimal, got {type(v)}')
                    raise NotImplementedError('Creating constants from RealDataType not implemented')
                else:
                    raise ValueError(f'Unrecognized type: {type(child_type)}')
            else:
                raise ValueError(f'{name}: missing initValue field: {elem.name}')
        return value

    def _create_array_value_v3(
            self,
            ws,
            name: str,
            data_type: ArrayDataType,
            init_value: Iterable,
            parent: ArObject | None = None,
    ):
        value = ArrayValue(name, data_type.ref, parent=parent)
        child_type = ws.find(data_type.type_ref)
        if child_type is None:
            raise ValueError(f'Invalid reference: {data_type.type_ref}')
        if not isinstance(init_value, Sequence):
            raise NotImplementedError(type(init_value))
        if len(init_value) < data_type.length:
            raise ValueError(f'{name}: too few elements in initValue, expected {data_type.length} items, got {len(init_value)}')
        for i, v in init_value[:data_type.length]:
            elem_name = f'{child_type.name}_{i}'
            if isinstance(child_type, IntegerDataType):
                if not isinstance(v, int):
                    raise ValueError(f'v: expected type int, got {type(v)}')
                value.elements.append(IntegerValue(elem_name, child_type.ref, v, value))
            elif isinstance(child_type, RecordDataType):
                if isinstance(v, Mapping) or isinstance(v, Iterable):
                    value.elements.append(self._create_record_value_v3(ws, elem_name, child_type, v, value))
                else:
                    raise ValueError(f'v: expected type Mapping or Iterable, got {type(v)}')
            elif isinstance(child_type, ArrayDataType):
                if not isinstance(v, Iterable):
                    raise ValueError(f'v: expected type Iterable, got {type(v)}')
                value.elements.append(self._create_array_value_v3(ws, elem_name, child_type, v, value))
            elif isinstance(child_type, BooleanDataType):
                if not isinstance(v, str) and not isinstance(v, int):
                    raise ValueError(f'v: expected type bool or str, got {type(v)}')
                v = bool(v)
                value.elements.append(BooleanValue(elem_name, child_type.ref, v, value))
            elif isinstance(child_type, StringDataType):
                if not isinstance(v, str):
                    raise ValueError(f'v: expected type str, got {type(v)}')
                value.elements.append(StringValue(elem_name, child_type.ref, v, value))
            elif isinstance(child_type, RealDataType):
                if not isinstance(v, float) and not isinstance(v, decimal.Decimal) and not isinstance(v, int):
                    raise ValueError(f'v: expected type int, float or Decimal, got {type(v)}')
                raise NotImplementedError('Creating constants from RealDataType not implemented')
            else:
                raise ValueError(f'Unrecognized type: {type(child_type)}')
        return value

    def _create_constant_v4(
            self,
            ws,
            name,
            data_type: ApplicationDataType | ImplementationDataType | None,
            init_value: str | int | float | bool | Iterable | Mapping,
            label: str,
            admin_data: AdminData | None = None,
    ):
        """
        If label argument is an empty string, the label of the created value is the same as
        the name of the constant.
        """
        if isinstance(label, str) and len(label) == 0:
            label = name
        builder = ValueBuilder()
        if data_type is None:
            value = builder.build(label, init_value)
        else:
            value = builder.build_from_data_type(data_type, init_value, label, ws)
        assert (value is not None)
        constant = Constant(name, value, parent=self, admin_data=admin_data)
        self.append(constant)
        return constant

    def create_text_value_constant(self, name: str, value: str):
        """AUTOSAR 4 text value constant"""
        constant = Constant(name, None, self)
        constant.value = TextValue(name, value, parent=constant)
        self.append(constant)
        return constant

    def create_numerical_value_constant(self, name: str, value: int | float):
        """AUTOSAR 4 numerical value constant"""
        constant = Constant(name, None, self)
        constant.value = NumericalValue(name, value, parent=constant)
        self.append(constant)
        return constant

    def create_application_value_constant(
            self,
            name: str,
            sw_value_cont: SwValueCont | None = None,
            sw_axis_cont: SwAxisCont | None = None,
            value_category: str | None = None,
            value_label: str | None = None,
    ):
        """
        (AUTOSAR4)
        Creates a new Constant containing a application value specification
        """
        ws = self.root_ws()
        assert (ws is not None)
        constant = Constant(name, None, self)
        inner_value = ApplicationValue(value_label, sw_value_cont, sw_axis_cont, value_category, parent=self)
        constant.value = inner_value
        self.append(constant)
        return constant

    def create_constant_from_value(self, name: str, value: ValueAR4):
        """
        (AUTOSAR4)
        Wraps an already created value in a constant object
        """
        if not isinstance(value, ValueAR4):
            raise ValueError(f'value argument must inherit from class ValueAR4 (got {type(value)})')
        ws = self.root_ws()
        assert (ws is not None)
        constant = Constant(name, value, self)
        self.append(constant)
        return constant

    def create_internal_data_constraint(
            self,
            name: str,
            lower_limit: int | float | str,
            upper_limit: int | float | str,
            lower_limit_type: str = 'CLOSED',
            upper_limit_type: str = 'CLOSED',
            admin_data: AdminData | None = None,
    ):
        ws = self.root_ws()
        assert (ws is not None)
        return self._check_and_create_data_constraint(
            ws,
            name,
            'internalConstraint',
            lower_limit,
            upper_limit,
            lower_limit_type,
            upper_limit_type,
            admin_data,
        )

    def create_physical_data_constraint(
            self,
            name: str,
            lower_limit: int | float | str,
            upper_limit: int | float | str,
            lower_limit_type: str = 'CLOSED',
            upper_limit_type: str = 'CLOSED',
            admin_data: AdminData | None = None,
    ):
        ws = self.root_ws()
        assert (ws is not None)
        return self._check_and_create_data_constraint(
            ws,
            name,
            'physicalConstraint',
            lower_limit,
            upper_limit,
            lower_limit_type,
            upper_limit_type,
            admin_data,
        )

    def create_sw_base_type(
            self,
            name: str,
            size: int | None = None,
            encoding: str | None = None,
            native_declaration: str | None = None,
            category: str = 'FIXED_LENGTH',
            admin_data: AdminData | None = None,
    ):
        """
        Creates a SwBaseType object
        """
        ws = self.root_ws()
        assert (ws is not None)

        if isinstance(admin_data, dict):
            admin_data_obj = ws.createAdminData(admin_data)
        else:
            admin_data_obj = admin_data
        if (admin_data_obj is not None) and not isinstance(admin_data_obj, AdminData):
            raise ValueError('adminData must be of type dict or AdminData')
        base_type = SwBaseType(name, size, encoding, native_declaration, category, self, admin_data)
        self.append(base_type)
        return base_type

    def create_base_type(
            self,
            name: str,
            size: int | None,
            encoding: str | None = None,
            native_declaration: str | None = None,
            admin_data: AdminData | None = None,
    ):
        """
        AUTOSAR4

        alias for createSwBaseType
        """
        return self.create_sw_base_type(name, size, encoding, native_declaration, admin_data=admin_data)

    def create_application_primitive_data_type(
            self,
            name: str,
            data_constraint: str = '',
            compu_method: str | None = None,
            unit: str | None = None,
            sw_calibration_access: str | None = None,
            category: str | None = None,
            admin_data: AdminData | None = None,
    ):
        """
        AUTOSAR4

        Creates a new ApplicationPrimitiveDataType in current package.

        name: <SHORT-NAME> (str)
        dataConstraint: Name or reference to autosar.datatype.DataConstraint object (or None). Default is to automatically create a constraint based on given compuMethod
        compuMethod: Name or reference to autosar.datatype.CompuMethod object (or None).
        swCalibrationAccess: Sets the SW-CALIBRATION-ACCESS property (str['NOT-ACCESSIBLE', 'READ-ONLY', 'READ-WRITE']).
        category: The category of this element (str)
        """
        ws = self.root_ws()
        assert (ws is not None)

        admin_data_obj = self._check_admin_data(admin_data)
        unit_obj = self._check_and_create_unit(ws, unit)
        data_constraint_obj, compu_method_obj = None, None
        if compu_method is not None:
            compu_method_obj = self._find_element_by_role(ws, compu_method, 'CompuMethod')
            if compu_method_obj is None:
                raise InvalidCompuMethodRef(compu_method)
        if data_constraint is not None:
            if len(data_constraint) == 0:
                data_constraint_name = self._create_data_constraint_name(ws, name)
                if compu_method_obj is not None:
                    data_constraint_obj = self._check_and_create_data_constraint_from_compu_method(ws, data_constraint_name, compu_method_obj)
            else:
                data_constraint_obj = self._find_element_by_role(ws, data_constraint, 'DataConstraint')
                if data_constraint_obj is None:
                    raise InvalidDataConstraintRef(data_constraint)

        unit_ref = None if unit_obj is None else unit_obj.ref
        compu_method_ref = None if compu_method_obj is None else compu_method_obj.ref
        data_constraint_ref = None if data_constraint_obj is None else data_constraint_obj.ref

        if sw_calibration_access is not None or data_constraint_ref is not None or compu_method_ref is not None or unit_ref is not None:
            variant_props = SwDataDefPropsConditional(
                sw_calibration_access=sw_calibration_access,
                data_constraint_ref=data_constraint_ref,
                compu_method_ref=compu_method_ref,
                unit_ref=unit_ref
            )
        else:
            variant_props = None
        data_type = ApplicationPrimitiveDataType(name, variant_props, category, parent=self, admin_data=admin_data_obj)
        self.append(data_type)
        return data_type

    def create_application_array_data_type(
            self,
            name: str,
            element: ApplicationArrayElement,
            sw_calibration_access: str | None = None,
            category: str = 'ARRAY',
            admin_data: AdminData | None = None,
    ):
        """
        AUTOSAR4

        Creates a new createApplicationArrayDataType in current package.

        name: <SHORT-NAME> (str)
        swCalibrationAccess: Sets the SW-CALIBRATION-ACCESS property (str['NOT-ACCESSIBLE', 'READ-ONLY', 'READ-WRITE']).
        element: <ELEMENT> (autosar.datatype.ApplicationArrayElement)
        category: The category of this element (str). Default='ARRAY'
        """
        ws = self.root_ws()
        assert (ws is not None)

        admin_data_obj = self._check_admin_data(admin_data)
        if sw_calibration_access is not None:
            variant_props = SwDataDefPropsConditional(
                sw_calibration_access=sw_calibration_access
            )
        else:
            variant_props = None
        data_type = ApplicationArrayDataType(name, element, variant_props, category, parent=self, admin_data=admin_data_obj)
        self.append(data_type)
        return data_type

    def create_application_record_data_type(
            self,
            name: str,
            elements: Iterable[tuple[str, str]] | None = None,
            sw_calibration_access: str | None = None,
            category: str = 'STRUCTURE',
            admin_data: AdminData | None = None,
    ):
        """
        (AUTOSAR4)
        Creates a new ImplementationDataType containing sub elements
        """
        ws = self.root_ws()
        assert (ws is not None)
        admin_data_obj = self._check_admin_data(admin_data)
        if sw_calibration_access is not None and len(sw_calibration_access) == 0:
            sw_calibration_access = ws.profile.sw_calibration_access_default

        if sw_calibration_access is not None:
            variant_props = SwDataDefPropsConditional(sw_calibration_access=sw_calibration_access)
        else:
            variant_props = None

        data_type = ApplicationRecordDataType(name, variant_props=variant_props, category=category, admin_data=admin_data_obj)
        if elements is not None:
            for element in elements:
                if not isinstance(element, tuple):
                    raise ValueError('Element must be a tuple')
                elem_name, elem_type_ref = element
                elem_type = ws.find(elem_type_ref, role='DataType')
                if elem_type is None:
                    raise InvalidDataTypeRef(elem_type_ref)
                data_type.create_element(elem_name, elem_type.ref)
        self.append(data_type)
        return data_type

    def create_implementation_data_type_ref(
            self,
            name: str,
            implementation_type_ref: str | None,
            lower_limit: int | float | str | None = None,
            upper_limit: int | float | str | None = None,
            value_table: Iterable[str | tuple] | None = None,
            bitmask: Iterable[tuple] | None = None,
            offset: int | float | None = None,
            scaling: int | float | None = None,
            unit: str | None = None,
            force_float: bool = False,
            data_constraint: str = '',
            sw_calibration_access: str = '',
            type_emitter: str | None = None,
            lower_limit_type: str | None = None,
            upper_limit_type: str | None = None,
            category: str = 'TYPE_REFERENCE',
            admin_data: AdminData | None = None,
    ) -> ImplementationDataType:
        """
        AUTOSAR4

        Creates an implementation data type that is a reference (typedef) of another implementation data type
        name: name of the new data type
        typeRef: reference to implementation data type
        """
        return self._create_implementation_data_type_internal(
            name,
            None,
            implementation_type_ref,
            lower_limit,
            upper_limit,
            value_table,
            bitmask,
            offset,
            scaling,
            unit,
            force_float,
            data_constraint,
            sw_calibration_access,
            type_emitter,
            lower_limit_type,
            upper_limit_type,
            category,
            admin_data
        )

    def create_implementation_data_type_ptr(
            self,
            name: str,
            base_type_ref: str,
            sw_impl_policy=None,
            category: str = 'DATA_REFERENCE',
            target_category: str = 'VALUE',
            admin_data: AdminData | None = None,
    ) -> ImplementationDataType:
        """
        Creates an implementation type that is a C-type pointer to another type
        """
        ws = self.root_ws()
        assert (ws is not None)

        admin_data_obj = self._check_admin_data(admin_data)

        target_props = SwPointerTargetProps(
            target_category,
            SwDataDefPropsConditional(base_type_ref=base_type_ref, sw_impl_policy=sw_impl_policy),
        )
        variant_props = SwDataDefPropsConditional(sw_pointer_target_props=target_props)
        implementation_data_type = ImplementationDataType(
            name,
            variant_props,
            category=category,
            parent=self,
            admin_data=admin_data_obj,
        )
        self.append(implementation_data_type)
        return implementation_data_type

    def create_implementation_array_data_type(
            self,
            name,
            implementation_type_ref: str,
            array_size: int | str | None,
            element_name: str | None = None,
            sw_calibration_access: str = '',
            type_emitter: str | None = None,
            category: str = 'ARRAY',
            target_category: str = 'TYPE_REFERENCE',
            admin_data: AdminData | None = None,
    ) -> ImplementationDataType:
        """
        (AUTOSAR4)
        Creates a new ImplementationDataType that references another type as an array
        """
        ws = self.root_ws()
        assert (ws is not None)
        if element_name is None:
            element_name = name
        if sw_calibration_access is not None and len(sw_calibration_access) == 0:
            sw_calibration_access = ws.profile.sw_calibration_access_default

        if implementation_type_ref.startswith('/'):
            data_type = ws.find(implementation_type_ref)
        else:
            data_type = ws.find(implementation_type_ref, role='DataType')
        if data_type is None:
            raise InvalidDataTypeRef(implementation_type_ref)

        new_type = ImplementationDataType(name, category=category, type_emitter=type_emitter, admin_data=admin_data)
        outer_props = SwDataDefPropsConditional(sw_calibration_access=sw_calibration_access)
        new_type.variant_props = [outer_props]
        inner_props = SwDataDefPropsConditional(implementation_type_ref=implementation_type_ref)
        sub_element = ImplementationDataTypeElement(element_name, target_category, array_size, variant_props=inner_props)
        new_type.sub_elements.append(sub_element)
        self.append(new_type)
        return new_type

    def create_implementation_data_type(
            self,
            name: str,
            base_type_ref: str | None,
            lower_limit: int | float | str | None = None,
            upper_limit: int | float | str | None = None,
            value_table: Iterable[str | tuple] | None = None,
            bitmask: Iterable[tuple] | None = None,
            offset: int | float | None = None,
            scaling: int | float | None = None,
            unit: str | None = None,
            force_float: bool = False,
            data_constraint: str = '',
            sw_calibration_access: str = '',
            type_emitter: str | None = None,
            lower_limit_type: str | None = None,
            upper_limit_type: str | None = None,
            category: str = 'VALUE',
            admin_data: AdminData | None = None,
    ) -> ImplementationDataType:
        return self._create_implementation_data_type_internal(
            name,
            base_type_ref,
            None,
            lower_limit,
            upper_limit,
            value_table,
            bitmask,
            offset,
            scaling,
            unit,
            force_float,
            data_constraint,
            sw_calibration_access,
            type_emitter,
            lower_limit_type,
            upper_limit_type,
            category,
            admin_data
        )

    def _create_implementation_data_type_internal(
            self,
            name: str,
            base_type_ref: str | None,
            implementation_type_ref: str | None,
            lower_limit: int | float | str | None,
            upper_limit: int | float | str | None,
            value_table: Iterable[str | tuple],
            bitmask: Iterable[tuple],
            offset: int | float | None,
            factor: int | float,
            unit: str,
            force_float: bool,
            data_constraint: str | None,
            sw_calibration_access: str | None,
            type_emitter: str | None,
            lower_limit_type: str | None,
            upper_limit_type: str | None,
            category: str,
            admin_data: AdminData | None,
    ) -> ImplementationDataType:
        """
        Creates an implementation data type that wraps a base type. Defaults to value type category
        """
        ws = self.root_ws()
        assert (ws is not None)

        lower_limit = self._convert_number(lower_limit)
        upper_limit = self._convert_number(upper_limit)

        if sw_calibration_access is not None and len(sw_calibration_access) == 0:
            sw_calibration_access = ws.profile.sw_calibration_access_default

        admin_data_obj = self._check_admin_data(admin_data)
        unit_obj = self._check_and_create_unit(ws, unit)

        if implementation_type_ref is not None:
            referenced_type = ws.find(implementation_type_ref)
            if referenced_type is None:
                raise InvalidDataTypeRef(implementation_type_ref)
        else:
            referenced_type = None

        compu_method_obj = self._check_and_create_compu_method(
            ws,
            self._create_compu_method_name(ws, name),
            unit_obj,
            lower_limit,
            upper_limit,
            offset,
            factor,
            bitmask,
            value_table,
            referenced_type,
            force_float,
        )
        if data_constraint is None:
            data_constraint_obj = None
        else:
            if not isinstance(data_constraint, str):
                raise ValueError('dataConstraint argument must be None or str')
            if len(data_constraint) == 0:
                # Automatically create a data constraint on empty string
                if compu_method_obj is not None:
                    data_constraint_obj = self._check_and_create_data_constraint_from_compu_method(
                        ws,
                        self._create_data_constraint_name(ws, name),
                        compu_method_obj,
                    )
                else:
                    if lower_limit is None and upper_limit is None:
                        data_constraint_obj = None
                    else:
                        if upper_limit is None:
                            raise ValueError('lowerLimit cannot be None')
                        if upper_limit is None:
                            raise ValueError('upperLimit cannot be None')
                        if lower_limit_type is None:
                            lower_limit_type = 'CLOSED'
                        if upper_limit_type is None:
                            upper_limit_type = 'CLOSED'
                        data_constraint_obj = self._check_and_create_data_constraint(
                            ws,
                            self._create_data_constraint_name(ws, name),
                            'internalConstraint',
                            lower_limit,
                            upper_limit,
                            lower_limit_type,
                            upper_limit_type,
                        )
            else:
                if data_constraint.startswith('/'):
                    data_constraint_obj = ws.find(data_constraint)
                else:
                    data_constraint_obj = ws.find(data_constraint, role='DataConstraint')
                if data_constraint_obj is None:
                    raise InvalidDataConstraintRef(data_constraint)

        unit_ref = None if unit_obj is None else unit_obj.ref
        compu_method_ref = None if compu_method_obj is None else compu_method_obj.ref
        data_constraint_ref = None if data_constraint_obj is None else data_constraint_obj.ref

        variant_props = SwDataDefPropsConditional(
            sw_calibration_access=sw_calibration_access,
            compu_method_ref=compu_method_ref,
            data_constraint_ref=data_constraint_ref,
            base_type_ref=base_type_ref,
            implementation_type_ref=implementation_type_ref,
            unit_ref=unit_ref,
        )
        implementation_data_type = ImplementationDataType(
            name,
            variant_props,
            type_emitter=type_emitter,
            category=category,
            parent=self,
            admin_data=admin_data_obj,
        )
        self.append(implementation_data_type)
        return implementation_data_type

    def create_implementation_record_data_type(
            self,
            name: str,
            elements: Iterable[tuple[str, str]],
            sw_calibration_access: str = '',
            category: str = 'STRUCTURE',
            admin_data: AdminData | None = None,
    ) -> ImplementationDataType:
        """
        (AUTOSAR4)
        Creates a new ImplementationDataType containing sub elements
        """
        ws = self.root_ws()
        assert (ws is not None)

        if sw_calibration_access is not None and len(sw_calibration_access) == 0:
            sw_calibration_access = ws.profile.sw_calibration_access_default

        if sw_calibration_access is not None:
            variant_props = SwDataDefPropsConditional(sw_calibration_access=sw_calibration_access)
        else:
            variant_props = None
        data_type = ImplementationDataType(name, variant_props, category=category, admin_data=admin_data)
        for element in elements:
            if not isinstance(element, tuple):
                raise ValueError('Element must be a tuple')
            element_name, elem_type_ref = element
            elem_type = ws.find(elem_type_ref, role='DataType')
            if elem_type is None:
                raise InvalidDataTypeRef(elem_type_ref)
            if isinstance(elem_type, ImplementationDataType):
                element_props = SwDataDefPropsConditional(implementation_type_ref=elem_type.ref)
            elif isinstance(elem_type, SwBaseType):
                element_props = SwDataDefPropsConditional(base_type_ref=elem_type.ref)
            else:
                raise NotImplementedError(type(elem_type))
            implementation_data_type_element = ImplementationDataTypeElement(
                element_name,
                'TYPE_REFERENCE',
                variant_props=element_props,
            )
            data_type.sub_elements.append(implementation_data_type_element)
        self.append(data_type)
        return data_type

    def create_unit(
            self,
            short_name: str,
            display_name: str | None = None,
            offset: int | float | None = None,
            scaling: int | float | None = None,
    ) -> Unit | None:
        ws = self.root_ws()
        assert (ws is not None)
        if ws.roles['Unit'] is None:
            unit_package = self
        else:
            unit_package = ws.find(ws.roles['Unit'])
        unit_elem = self._check_and_create_unit(ws, short_name, display_name, scaling, offset, unit_package)
        return unit_elem

    def create_compu_method_linear(
            self,
            name: str,
            offset: int | float | None,
            scaling: int | float,
            lower_limit: int | float | str | None = None,
            upper_limit: int | float | str | None = None,
            lower_limit_type: str = 'CLOSED',
            upper_limit_type: str = 'CLOSED',
            unit: str | None = None,
            default_value: int | float | str | None = None,
            label: str = 'SCALING',
            force_float: bool = True,
            category: str = 'LINEAR',
            admin_data: AdminData | None = None,
    ) -> CompuMethod:
        """
        Alias for createCompuMethodRational
        """
        return self.create_compu_method_rational(
            name,
            offset,
            scaling,
            lower_limit,
            upper_limit,
            lower_limit_type,
            upper_limit_type,
            unit,
            default_value,
            label,
            force_float,
            category=category,
            admin_data=admin_data,
        )

    def create_compu_method_rational_phys(
            self,
            name: str,
            offset: int | float | None,
            scaling: int | float,
            lower_limit: int | float | str | None = None,
            upper_limit: int | float | str | None = None,
            lower_limit_type: str = 'CLOSED',
            upper_limit_type: str = 'CLOSED',
            unit: str | None = None,
            default_value: int | float | str | None = None,
            label: str = 'SCALING',
            force_float: bool = True,
            use_int_to_phys: bool = False,
            use_phys_to_int: bool = True,
            category: str = 'LINEAR',
            admin_data: AdminData | None = None,
    ) -> CompuMethod:
        """
        Alias for createCompuMethodRational but creates a PHYSICAL-TO-INTERNAL mapping by default
        """
        return self.create_compu_method_rational(
            name,
            offset,
            scaling,
            lower_limit,
            upper_limit,
            lower_limit_type,
            upper_limit_type,
            unit,
            default_value,
            label,
            force_float,
            use_int_to_phys,
            use_phys_to_int,
            category,
            admin_data,
        )

    def create_compu_method_rational(
            self,
            name: str,
            offset: int | float,
            scaling: int | float,
            lower_limit: int | float | str | None = None,
            upper_limit: int | float | str | None = None,
            lower_limit_type: str = 'CLOSED',
            upper_limit_type: str = 'CLOSED',
            unit: str | None = None,
            default_value: int | float | str | None = None,
            label: str = 'SCALING',
            force_float: bool = False,
            use_int_to_phys: bool = True,
            use_phys_to_int: bool = False,
            category: str = 'LINEAR',
            admin_data: AdminData | None = None,
    ) -> CompuMethod:
        """
        Creates a new CompuMethodRational object and appends it to the package with package-role 'CompuMethod'

        name: <SHORT-NAME> (str)
        offset: offset (int or float)
        scaling: scaling factor (int, float or rational number). This together with offset creates the numerator and denominator.
        lowerLimit: <LOWER-LIMIT> (int). Default = None.
        uppwerLimit: <UPPER-LIMIT> (int). Default = None.
        lowerLimitType: "INTERVAL-TYPE" of lowerLimit, str['OPEN', 'CLOSED']. Default='CLOSED'. Only applies when lowerLimit is not None.
        upperLimitType: "INTERVAL-TYPE" of upperLimit, str['OPEN', 'CLOSED']. Default='CLOSED'. Only applies when lowerLimit is not None.
        unit: Name of the unit (str). Default = None
        defaultValue: default value for the computation (None, int, float, str). Default = None.
        label: Label for the internally created <COMPU-SCALE> (str). Default = 'SCALING'.
        forceFloat: Forces numerator to become a floating point number (bool). Default = False.
        intToPhys: Enable internal-to-physical computation (bool). Default = True.
        physToInt: Enable physical-to-internal computation (bool). Default = False.
        category: <CATEGORY> of the CompuMethodRational (str). Default = 'LINEAR'.
        adminData: <ADMIN-DATA> for <COMPU-METHOD> (dict). Default = None.

        """
        ws = self.root_ws()
        assert (ws is not None)

        if ws.roles['CompuMethod'] is None:
            compu_method_package = self
        else:
            compu_method_package = ws.find(ws.roles['CompuMethod'])

        unit_ref = None
        unit_obj = self._check_and_create_unit(ws, unit)
        if unit_obj is not None:
            unit_ref = unit_obj.ref

        admin_data_obj = self._check_admin_data(admin_data)

        compu_method = CompuMethod(name, use_int_to_phys, use_phys_to_int, unit_ref, category, compu_method_package, admin_data_obj)
        numerator, denominator = self._calc_numerator_denominator(scaling, force_float)
        if use_int_to_phys:
            compu_method.int_to_phys.create_rational_scaling(
                offset,
                numerator,
                denominator,
                lower_limit,
                upper_limit,
                lower_limit_type,
                upper_limit_type,
                label=label
            )
            if default_value is not None:
                compu_method.int_to_phys.default_value = default_value
        elif use_phys_to_int:
            compu_method.phys_to_int.create_rational_scaling(
                offset,
                numerator,
                denominator,
                lower_limit,
                upper_limit,
                lower_limit_type,
                upper_limit_type,
                label=label
            )
            if default_value is not None:
                if use_int_to_phys:
                    compu_method.int_to_phys.default_value = default_value
                elif use_phys_to_int:
                    compu_method.phys_to_int.default_value = default_value

        compu_method_package.append(compu_method)
        return compu_method

    def create_compu_method_const(
            self,
            name: str,
            value_table: Iterable[str | tuple],
            unit: str | None = None,
            default_value: int | float | str | None = None,
            category: str = 'TEXTTABLE',
            admin_data: AdminData | None = None,
    ) -> CompuMethod:
        use_int_to_phys, use_phys_to_int = True, False

        ws = self.root_ws()
        assert (ws is not None)

        if ws.roles['CompuMethod'] is None:
            compu_method_package = self
        else:
            compu_method_package = ws.find(ws.roles['CompuMethod'])
        unit_ref = None
        unit_obj = self._check_and_create_unit(ws, unit)
        if unit_obj is not None:
            unit_ref = unit_obj.ref
        if isinstance(admin_data, dict):
            admin_data = create_admin_data(admin_data)

        compu_method = CompuMethod(
            name,
            use_int_to_phys,
            use_phys_to_int,
            unit_ref,
            category,
            compu_method_package,
            admin_data,
        )
        compu_method.int_to_phys.create_value_table(value_table)
        if default_value is not None:
            compu_method.int_to_phys.default_value = default_value

        compu_method_package.append(compu_method)
        return compu_method

    def create_data_type_mapping_set(self, name: str, admin_data: AdminData | None = None) -> DataTypeMappingSet:
        data_type_mapping_set = DataTypeMappingSet(name, admin_data=admin_data)
        self.append(data_type_mapping_set)
        return data_type_mapping_set

    @staticmethod
    def _calc_numerator_denominator(
            scaling_factor: float | int,
            force_float: bool = False,
    ) -> tuple[int | float, int | float]:
        if force_float:
            numerator, denominator = float(scaling_factor), 1
        else:
            f = Fraction.from_float(scaling_factor)
            if f.denominator > 10000:  # use the float version in case it's not a rational number
                numerator, denominator = float(scaling_factor), 1
            else:
                numerator, denominator = f.numerator, f.denominator
        return numerator, denominator

    def _check_and_create_compu_method(
            self,
            ws,
            name: str,
            unit_obj: Unit,
            lower_limit: int | float | str,
            upper_limit: int | float | str,
            offset: int | float | None,
            scaling: int | float,
            bitmask_table: Iterable[tuple] | None,
            value_table: Iterable[str | tuple],
            referenced_type: ApplicationDataType | ImplementationDataType | None,
            force_float_scaling: bool,
            use_category: bool = True,
            auto_label: bool = True,
    ) -> CompuMethod | None:
        """
        Returns CompuMethod object from the package with role 'CompuMethod'.
        If no CompuMethod exists with that name it will be created and then returned.
        """
        if name is None:
            return None

        category = None
        computation = Computation()
        if bitmask_table is not None:
            category = 'BITFIELD_TEXTTABLE'
            computation.create_bit_mask(bitmask_table)
        elif value_table is not None:
            category = 'TEXTTABLE'
            computation.create_value_table(value_table, auto_label)
        elif offset is not None and scaling is not None:
            category = 'LINEAR'
            numerator, denominator = self._calc_numerator_denominator(scaling, force_float_scaling)
            if (lower_limit is None) and (referenced_type is not None) and (referenced_type.data_constraint_ref is not None):
                constraint = ws.find(referenced_type.data_constraint_ref)
                if constraint is None:
                    raise InvalidDataConstraintRef
                lower_limit = constraint.lower_limit
            if (upper_limit is None) and (referenced_type is not None) and (referenced_type.data_constraint_ref is not None):
                constraint = ws.find(referenced_type.data_constraint_ref)
                if constraint is None:
                    raise InvalidDataConstraintRef
                upper_limit = constraint.upper_limit
            computation.create_rational_scaling(offset, numerator, denominator, lower_limit, upper_limit)
        if category is None:
            return None  # Creating a compu method does not seem necessary

        compu_method_package = None
        if ws.roles['CompuMethod'] is not None:
            compu_method_package = ws.find(ws.roles['CompuMethod'])
        if compu_method_package is None:
            raise RuntimeError("No package found with role='CompuMethod'")
        compu_method_obj = compu_method_package.find(name)
        if compu_method_obj is not None:  # Element already exists with that name?
            return compu_method_obj
        unit_ref = None if unit_obj is None else unit_obj.ref

        use_int_to_phys, use_phys_to_int = True, False
        if not use_category:
            category = None
        compu_method_obj = CompuMethod(name, use_int_to_phys, use_phys_to_int, unit_ref, category, compu_method_package)
        compu_method_obj.int_to_phys = computation
        compu_method_package.append(compu_method_obj)
        return compu_method_obj

    def _check_and_create_data_constraint_from_compu_method(
            self,
            ws,
            name: str,
            compu_method_obj: CompuMethod,
    ) -> DataConstraint | None:
        constraint_type = 'internalConstraint'
        if compu_method_obj.category == 'BITFIELD_TEXTTABLE':
            lower_limit = 0
            tmp = compu_method_obj.int_to_phys.upper_limit
            upper_limit = 2 ** int.bit_length(tmp) - 1
        else:
            lower_limit = compu_method_obj.int_to_phys.lower_limit
            upper_limit = compu_method_obj.int_to_phys.upper_limit
        if (lower_limit is not None) and upper_limit is not None:
            return self._check_and_create_data_constraint(ws, name, constraint_type, lower_limit, upper_limit)
        else:
            return None

    def _check_and_create_data_constraint(
            self,
            ws,
            name: str,
            constraint_type: str,
            lower_limit: int | float | str,
            upper_limit: int | float | str,
            lower_limit_type: str = 'CLOSED',
            upper_limit_type: str = 'CLOSED',
            admin_data: AdminData | None = None,
    ) -> DataConstraint | None:
        if name is None:
            return None
        data_constraint_package: Package | None = None
        if ws.roles['DataConstraint'] is not None:
            data_constraint_package = ws.find(ws.roles['DataConstraint'])
        if data_constraint_package is None:
            raise RuntimeError('No package found with role=DataConstraint')
        data_constraint_obj = data_constraint_package.find(name)
        if data_constraint_obj is not None:  # Element already exists with that name?
            return data_constraint_obj
        else:
            return self._create_data_constraint_in_package(
                data_constraint_package,
                name,
                constraint_type,
                lower_limit,
                upper_limit,
                lower_limit_type,
                upper_limit_type,
                admin_data,
            )

    @staticmethod
    def _find_element_by_role(ws, name: str, role: str):
        if name.startswith('/'):
            return ws.find(name, role=role)
        else:
            return ws.find(name, role=role)

    def _create_data_constraint_in_package(
            self,
            data_constraint_package: 'Package',
            name: str,
            constraint_type: str,
            lower_limit: int | float | str,
            upper_limit: int | float | str,
            lower_limit_type: str,
            upper_limit_type: str,
            admin_data: AdminData | None,
    ) -> DataConstraint:
        """
        Returns DataConstraint object from the package with role 'DataConstraint'.
        If no DataConstraint exists with that name it will be created and then returned.
        """
        rules = [{
            'type': constraint_type,
            'lowerLimit': lower_limit,
            'upperLimit': upper_limit,
            'lowerLimitType': lower_limit_type,
            'upperLimitType': upper_limit_type,
        }]
        constraint = DataConstraint(name, rules, parent=self, admin_data=admin_data)
        data_constraint_package.append(constraint)
        return constraint

    @staticmethod
    def _check_admin_data(admin_data: AdminData | dict):
        if isinstance(admin_data, dict):
            admin_data_obj = create_admin_data(admin_data)
        else:
            admin_data_obj = admin_data
        if (admin_data_obj is not None) and not isinstance(admin_data_obj, AdminData):
            raise ValueError('adminData must be of type dict or AdminData')
        return admin_data_obj

    def _create_compu_method_and_unit_v3(
            self,
            ws,
            name: str,
            lower_limit: int | float | str | None,
            upper_limit: int | float | str | None,
            value_table: Iterable[str | tuple],
            bitmask: Iterable[tuple] | None,
            offset: int | float | None,
            scaling: int | float,
            unit: str | None,
            force_float_scaling: bool,
    ):
        """
        AUTOSAR3:

        If both compuMethod and unit: Returns (compuMethodRef, unitRef)
        Else if compuMethod only: Returns (compuMethodRef, None)
        Else: Returns (None, None)
        """
        unit_package = None
        unit_elem = None
        assert (ws is not None)
        if ws.roles['CompuMethod'] is not None:
            semantics_package = ws.find(ws.roles['CompuMethod'])
            if semantics_package is None:
                raise RuntimeError('No package found with role=CompuMethod')
        if ws.roles['Unit'] is not None:
            unit_package = ws.find(ws.roles['Unit'])
            if unit_package is None:
                raise RuntimeError('No package found with role=Unit')

        if ((lower_limit is None) and (upper_limit is None) and (value_table is None) and (bitmask is None)
                and (offset is None) and (scaling is None) and (unit is None)):
            return None

        if unit is not None:
            unit_elem = self._check_and_create_unit(ws, unit, unit_package=unit_package)
        compu_method_elem = self._check_and_create_compu_method(
            ws,
            self._create_compu_method_name(ws, name),
            unit_elem,
            lower_limit,
            upper_limit,
            offset,
            scaling,
            None,
            value_table,
            None,
            force_float_scaling,
            use_category=False,
            auto_label=False,
        )
        if (compu_method_elem is not None) and (unit_elem is not None):
            compu_method_elem.unit_ref = unit_elem.ref
        return None if compu_method_elem is None else compu_method_elem.ref

    def _check_and_create_unit(
            self,
            ws,
            short_name: str,
            display_name: str | None = None,
            factor: int | float | None = None,
            offset: int | float | None = None,
            unit_package: 'Package | None' = None,
    ) -> Unit | None:
        if short_name is None:
            return None
        if unit_package is None:
            unit_package = ws.find(ws.roles['Unit'])
            if unit_package is None:
                raise RuntimeError('No package found with role=Unit')
        assert (isinstance(unit_package, Package))
        unit_elem = unit_package.find(short_name)
        if unit_elem is None:
            unit_elem = self._create_unit_in_package(unit_package, short_name, display_name, factor, offset)
        return unit_elem

    @staticmethod
    def _create_unit_in_package(
            unit_package: 'Package',
            short_name: str,
            display_name: str | None = None,
            factor: int | float | None = None,
            offset: int | float | None = None,
    ) -> Unit:
        if display_name is None:
            display_name = short_name
        unit_elem = Unit(short_name, display_name, factor, offset)
        unit_package.append(unit_elem)
        return unit_elem

    @staticmethod
    def _convert_number(number: int | float | str | None) -> int | float | str | None:
        """
        Attempts to convert argument to int.
        If that fails it tries to convert to float.
        If that fails it returns the argument as a string.
        """
        retval = None
        if number is not None:
            try:
                retval = int(number)
            except ValueError:
                try:
                    retval = float(number)
                except ValueError:
                    retval = str(number)
        return retval

    @staticmethod
    def _create_compu_method_name(ws, name: str) -> str:
        return name + ws.profile.compu_method_suffix

    @staticmethod
    def _create_data_constraint_name(ws, name: str) -> str:
        return name + ws.profile.data_constraint_suffix
