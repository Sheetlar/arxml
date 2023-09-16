from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Iterable

from autosar.swc_implementation import SwcImplementation
from autosar.ar_object import ArObject
from autosar.base import InvalidPortInterfaceRef, split_ref, InvalidPortRef, InvalidMappingRef
from autosar.element import Element
from autosar.port import Port, ProvidePort, RequirePort
from autosar.portinterface import SenderReceiverInterface

if TYPE_CHECKING:
    from autosar import Template
    from autosar.behavior import InternalBehaviorCommon


class ComponentType(Element):
    """
    Base class for all software component prototype classes.
    """

    def __init__(self, name: str, parent: ArObject | None = None):
        super().__init__(name, parent)
        self.require_ports: list[RequirePort] = []
        self.provide_ports: list[ProvidePort] = []

    def find(self, ref: str, *args, **kwargs):
        ref = ref.partition('/')
        for port in self.require_ports:
            if port.name == ref[0]:
                return port
        for port in self.provide_ports:
            if port.name == ref[0]:
                return port
        return None

    def append(self, elem: Port):
        if isinstance(elem, RequirePort):
            self.require_ports.append(elem)
            elem.parent = self
        elif isinstance(elem, ProvidePort):
            self.provide_ports.append(elem)
            elem.parent = self
        else:
            raise ValueError(f'Unexpected type: {type(elem)}')

    def __getitem__(self, key):
        return self.find(key)

    def create_provide_port(self, name: str, port_interface_ref: str, **kwargs):
        """
        Creates a provide port on this ComponentType
        The ComponentType must have a valid ref (must belong to a valid package in a valid workspace).
        Parameters:

        - name: Name of the port
        - portInterfaceRef: Reference to existing port interface
        - comspec: This is an advanced way to create comspecs directly in the port.

        For SenderReceiver port interfaces which contains exactly one data element there is another way of creating ComSpecs.
        - comspec: Should be left as None.
        - initValue: Used to set an init value literal.
        - initValueRef: Used instead of initValue when you want to reference an existing constant specification.
        - aliveTimeout: Alive timeout setting (in seconds).
        - queueLength (None or int): Length of queue (only applicable for port interface with isQueued property).
        - canInvalidate: Invalidation property (boolean). (AUTOSAR3 only?)

        For Parameter port interfaces you can use these parameters:
        - initValue (int, float or str): Init value literal

        For ModeSwitch port interfaces these parameters are valid for building port comspec:
        - enhancedMode (bool): Sets the enhancedMode (API) property
        - modeSwitchAckTimeout (None or int): Sets the modeSwitchAckTimeout property (milliseconds)
        - queueLength (None or int): Length of call queue on the mode user side.

        For NvDataInterface port interfaces which contains one data element there is another way of creating ComSpecs.
        - ramBlockInitValue (int, float, str): Used to set an init value literal.
        - ramBlockInitValueRef (str): Used when you want an existing constant specification as your initValue.
        - romBlockInitValue (int, float, str): Used to set an init value literal.
        - romBlockInitValueRef (str): Used when you want an existing constant specification as your initValue.
        """

        com_spec = kwargs.get('comspec', None)
        if com_spec is not None:
            if isinstance(com_spec, Mapping):
                com_spec_list = [com_spec]
            elif isinstance(com_spec, Iterable):
                com_spec_list = list(com_spec)
            else:
                raise ValueError('comspec argument must be of type dict or list')
        else:
            com_spec_list = None
        assert (self.ref is not None)
        ws = self.root_ws()
        assert (ws is not None)
        port_interface = ws.find(port_interface_ref)
        if port_interface is None:
            raise InvalidPortInterfaceRef(port_interface_ref)
        if com_spec_list is None:
            com_spec_dict = kwargs if len(kwargs) > 0 else None
            port = ProvidePort(name, port_interface.ref, com_spec_dict, parent=self)
        else:
            port = ProvidePort(name, port_interface.ref, com_spec_list, parent=self)
        assert (isinstance(port, Port))
        self.provide_ports.append(port)
        return port

    def create_require_port(self, name: str, port_interface_ref: str, **kwargs):
        """
        Creates a require port on this ComponentType
        The ComponentType must have a valid ref (must belong to a valid package in a valid workspace).
        Parameters:

        - name: Name of the port
        - portInterfaceRef: Reference to existing port interface

        For SenderReceiver port interfaces which contains one data element there is another way of creating ComSpecs.
        - initValue (int, float, str): Used to set an init value literal.
        - initValueRef (str): Used when you want an existing constant specification as your initValue.
        - aliveTimeout(int): Alive timeout setting (in seconds).
        - queueLength(int): Length of queue (only applicable for port interface with isQueued property).
        - canInvalidate(bool): Invalidation property (boolean). (AUTOSAR3 only)

        For Parameter port interfaces you can use these parameters:
        - initValue (int, float or str): Init value literal

        For ModeSwitch port interfaces these parameters are valid:
        - modeGroup: The name of the mode group in the port interface (None or str)
        - enhancedMode: sets the enhancedMode property  (bool)
        - supportAsync: sets the supportAsync property  (bool)

        For NvDataInterface port interfaces which contains one data element there is another way of creating ComSpecs.
        - initValue (int, float, str): Used to set an init value literal.
        - initValueRef (str): Used when you want an existing constant specification as your initValue.
        """
        com_spec = kwargs.get('comspec', None)
        assert (self.ref is not None)
        ws = self.root_ws()
        assert (ws is not None)
        port_interface = ws.find(port_interface_ref)
        if port_interface is None:
            raise InvalidPortInterfaceRef(port_interface_ref)
        if com_spec is None:
            com_spec_dict = kwargs if len(kwargs) > 0 else None
            port = RequirePort(name, port_interface.ref, com_spec_dict, parent=self)
        else:
            port = RequirePort(name, port_interface.ref, com_spec, parent=self)
        assert (isinstance(port, Port))
        self.require_ports.append(port)
        return port

    def apply(self, template: Template, **kwargs):
        """
        Applies template to this component
        This is typically used for port templates
        """
        if len(kwargs) == 0:
            template.apply(self)
        else:
            template.apply(self, **kwargs)
        template.usage_count += 1

    def copy_port(self, other_port: ProvidePort | RequirePort):
        """
        Adds a copy of a port (from another component)
        """
        self.append(other_port.copy())

    def mirror_port(self, other_port: ProvidePort | RequirePort):
        """
        Adds a mirrored copy of a port (from another component)
        """
        self.append(other_port.mirror())


class AtomicSoftwareComponent(ComponentType):
    """
    base class for ApplicationSoftwareComponent and ComplexDeviceDriverComponent
    """

    def __init__(self, name: str, parent: ArObject | None = None):
        super().__init__(name, parent)
        self.behavior: InternalBehaviorCommon | None = None
        self.implementation: SwcImplementation | None = None

    def find(self, ref: str, **kwargs):
        ws = self.root_ws()
        ref = ref.partition('/')
        for port in self.require_ports:
            if port.name == ref[0]:
                return port
        for port in self.provide_ports:
            if port.name == ref[0]:
                return port
        if (ws is not None) and (ws.version >= 4.0) and (self.behavior is not None):
            if self.behavior.name == ref[0]:
                if len(ref[2]) > 0:
                    return self.behavior.find(ref[2])
                else:
                    return self.behavior
        return None


class ApplicationSoftwareComponent(AtomicSoftwareComponent):
    @staticmethod
    def tag(version: float | None = None):
        if version is not None and version >= 4.0:
            return 'APPLICATION-SW-COMPONENT-TYPE'
        return 'APPLICATION-SOFTWARE-COMPONENT-TYPE'

    def __init__(self, name, parent=None):
        super().__init__(name, parent)


class ComplexDeviceDriverComponent(AtomicSoftwareComponent):
    @staticmethod
    def tag(version: float | None = None):
        if version is not None and version >= 4.0:
            return 'COMPLEX-DEVICE-DRIVER-SW-COMPONENT-TYPE'
        return 'COMPLEX-DEVICE-DRIVER-COMPONENT-TYPE'

    def __init__(self, name, parent=None):
        super().__init__(name, parent)


class ServiceComponent(AtomicSoftwareComponent):
    @staticmethod
    def tag(version: float | None = None):
        if version is not None and version >= 4.0:
            return 'SERVICE-COMPONENT-TYPE'
        return 'SERVICE-SW-COMPONENT-TYPE'

    def __init__(self, name, parent=None):
        super().__init__(name, parent)


class ParameterComponent(AtomicSoftwareComponent):
    @staticmethod
    def tag(version: float | None = None):
        if version is not None and version >= 4.0:
            return 'CALPRM-COMPONENT-TYPE'
        return 'PARAMETER-SW-COMPONENT-TYPE'

    def __init__(self, name, parent=None):
        super().__init__(name, parent)


class SensorActuatorComponent(AtomicSoftwareComponent):
    @staticmethod
    def tag(*_):
        return "SENSOR-ACTUATOR-SW-COMPONENT-TYPE"

    def __init__(self, name, parent=None):
        super().__init__(name, parent)


class NvBlockComponent(AtomicSoftwareComponent):
    @staticmethod
    def tag(*_):
        return "NV-BLOCK-SW-COMPONENT-TYPE"

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.nv_block_descriptors = []

    def find(self, ref, **kwargs):
        parts = ref.partition('/')
        for elem in self.nv_block_descriptors:
            if elem.name == parts[0]:
                if len(parts[2]) > 0:
                    return elem.find(parts[2])
                else:
                    return elem
        return super().find(ref)


class CompositionComponent(ComponentType):
    """
    Composition Component
    """

    @staticmethod
    def tag(version: float | None = None):
        if version is not None and version >= 4.0:
            return 'COMPOSITION-SW-COMPONENT-TYPE'
        return 'COMPOSITION-TYPE'

    def __init__(self, name: str, parent: ArObject | None = None):
        super().__init__(name, parent)
        self.components: list[ComponentPrototype] = []
        self.assembly_connectors: list[AssemblyConnector] = []
        self.delegation_connectors: list[DelegationConnector] = []
        self.data_type_mapping_refs: list[str] = []

    def find(self, ref: str, **kwargs):
        parts = ref.partition('/')
        for elem in self.components:
            if elem.name == parts[0]:
                return elem
        for elem in self.assembly_connectors:
            if elem.name == parts[0]:
                return elem
        for elem in self.delegation_connectors:
            if elem.name == parts[0]:
                return elem
        return super().find(ref)

    def create_component_ref(self, component_ref: str):
        """
        Alias for createComponentPrototype
        """
        return self.create_component_prototype(component_ref)

    def create_component_prototype(self, component_ref: str, name: str | None = None):
        """
        creates a new ComponentPrototype object and appends it to the CompositionComponent
        """
        ws = self.root_ws()
        component = ws.find(component_ref)
        if component is None:
            raise ValueError('invalid reference: ' + component_ref)
        if name is None:
            name = component.name
        elem = ComponentPrototype(name, component.ref, self)
        self.components.append(elem)
        return elem

    def create_connector(self, port_ref_1: str, port_ref_2: str):
        """
        creates a connector between an inner and outer port or between two inner ports
        portRef1 and portRef2 can be of either formats:
        'componentName/portName', 'portName' or 'componentRef/portName'
        """
        ws = self.root_ws()
        assert (ws is not None)
        port1, component1 = self._analyze_port_ref(ws, port_ref_1)
        port2, component2 = self._analyze_port_ref(ws, port_ref_2)

        if isinstance(component1, ComponentPrototype) and isinstance(component2, ComponentPrototype):
            # create an assembly port between the two ports
            if isinstance(port1, RequirePort) and isinstance(port2, ProvidePort):
                requester_component, provider_component = component1, component2
                require_port, provide_port = port1, port2
            elif isinstance(port2, RequirePort) and isinstance(port1, ProvidePort):
                requester_component, provider_component = component2, component1
                require_port, provide_port = port2, port1
            elif isinstance(port2, RequirePort) and isinstance(port1, RequirePort):
                raise ValueError('Cannot create assembly connector between two require ports')
            else:
                raise ValueError('Cannot create assembly connector between two provide ports')
            return self._create_assembly_port_internal(provider_component, provide_port, requester_component, require_port)
        elif isinstance(component1, ComponentPrototype):
            # create a delegation port between port1 and port2
            inner_component, inner_port = component1, port1
            outer_port = port2
        elif component1 is self and isinstance(component2, ComponentPrototype):
            # create a delegation port between port1 and port2
            inner_component, inner_port = component2, port2
            outer_port = port1
        else:
            raise ValueError(f'Invalid connector arguments ("{port_ref_1}", "{port_ref_2}")')
        # create delegation connector
        return self._create_delegation_connector_internal(inner_component, inner_port, outer_port)

    def _create_assembly_port_internal(
            self,
            provider_component: ComponentPrototype,
            provide_port: ProvidePort,
            requester_component: ComponentPrototype,
            require_port: RequirePort,
    ):
        connector_name = '_'.join([provider_component.name, provide_port.name, requester_component.name, require_port.name])
        connector = AssemblyConnector(
            connector_name,
            ProviderInstanceRef(provider_component.ref, provide_port.ref),
            RequesterInstanceRef(requester_component.ref, require_port.ref),
        )
        if self.find(connector_name) is not None:
            raise ValueError(f'Connector "{connector_name}" already exists')
        self.assembly_connectors.append(connector)
        return connector

    def _create_delegation_connector_internal(
            self,
            inner_component: ComponentPrototype,
            inner_port: Port,
            outer_port: Port,
    ):
        if isinstance(outer_port, ProvidePort):
            connector_name = '_'.join([inner_component.name, inner_port.name, outer_port.name])
        else:
            connector_name = '_'.join([outer_port.name, inner_component.name, inner_port.name])
        connector = DelegationConnector(
            connector_name,
            InnerPortInstanceRef(inner_component.ref, inner_port.ref),
            OuterPortRef(outer_port.ref),
        )
        self.delegation_connectors.append(connector)
        return connector

    def _analyze_port_ref(self, ws, port_ref: str):
        parts = split_ref(port_ref)
        if len(parts) > 1:
            if len(parts) == 2:
                # assume format 'componentName/portName' where componentName is an inner component
                for inner_component in self.components:
                    component = ws.find(inner_component.type_ref)
                    if component is None:
                        raise ValueError(f'Invalid reference: {inner_component.type_ref}')
                    if component.name == parts[0]:
                        port = component.find(parts[1])
                        if port is None:
                            raise ValueError(f'Component "{component.name}" does not seem to have port with name "{parts[1]}"')
                        component = inner_component
                        break
                else:
                    raise ValueError(f'Component with port ref "{port_ref}" not found')
            else:
                # assume portRef is a full reference
                port = ws.find(port_ref)
                if port is None:
                    raise InvalidPortRef(port_ref)
                if not isinstance(port, Port):
                    raise ValueError(f'Reference "{parts[0]}" is not a port or duplicate references exists in the workspace')
                parent_ref = port.parent.ref
                for inner_component in self.components:
                    if inner_component.type_ref == parent_ref:
                        component = inner_component
                        break
                else:
                    raise ValueError(f'Reference "{port_ref}" does not seem to be a port where the (parent) component is part of this composition')
        else:
            port = self.find(parts[0])
            component = self
        if port is None:
            raise ValueError(f'Component "{component.name}" does not seem to have port with name "{parts[0]}"')
        if not isinstance(port, Port):
            raise ValueError(f'Port name "{parts[0]}" is ambiguous. This might be due to duplicate references exists in the workspace')
        return port, component

    def auto_connect(self):
        """
        Connect ports with matching names and matching port interface references
        """
        ws = self.root_ws()
        assert (ws is not None)
        inner_require_port_map, inner_provide_port_map = self._build_inner_port_map(ws)
        self._auto_create_assembly_connectors(inner_require_port_map, inner_provide_port_map)
        self._auto_create_delegation_connectors(inner_require_port_map, inner_provide_port_map)

    def _build_inner_port_map(self, ws) -> tuple[
        dict[str, list[tuple[ComponentPrototype, RequirePort]]],
        dict[str, list[tuple[ComponentPrototype, ProvidePort]]],
    ]:
        require_ports = {}
        provide_ports = {}
        # build inner map
        for inner_component in self.components:
            actual_component = ws.find(inner_component.type_ref)
            if actual_component is None:
                raise ValueError(f'Invalid reference: {inner_component.type_ref}')
            for inner_port in actual_component.require_ports:
                if inner_port.name not in require_ports:
                    require_ports[inner_port.name] = []
                require_ports[inner_port.name].append((inner_component, inner_port))
            for inner_port in actual_component.provide_ports:
                if inner_port.name not in provide_ports:
                    provide_ports[inner_port.name] = []
                provide_ports[inner_port.name].append((inner_component, inner_port))
        return require_ports, provide_ports

    def _auto_create_assembly_connectors(
            self,
            inner_require_port_map: dict[str, list[tuple[ComponentPrototype, RequirePort]]],
            inner_provide_port_map: dict[str, list[tuple[ComponentPrototype, ProvidePort]]],
    ):
        for name in sorted(inner_provide_port_map.keys()):
            if len(inner_provide_port_map[name]) > 1:
                self._logger.warning(f'Multiple components are providing the same port "{name}: '
                                     f'{", ".join(x.name for x, _ in inner_provide_port_map[name])}"')
            provider_component, provide_port = inner_provide_port_map[name][0]
            if name in inner_require_port_map:
                for requester_component, require_port in inner_require_port_map[name]:
                    if require_port.port_interface_ref == provide_port.port_interface_ref:
                        self._create_assembly_port_internal(provider_component, provide_port, requester_component, require_port)

    def _auto_create_delegation_connectors(
            self,
            inner_require_port_map: dict[str, list[tuple[ComponentPrototype, RequirePort]]],
            inner_provide_port_map: dict[str, list[tuple[ComponentPrototype, ProvidePort]]],
    ):
        for outer_port in sorted(self.provide_ports, key=lambda x: x.name):
            if outer_port.name and outer_port.name in inner_provide_port_map:
                for inner_component, inner_port in inner_provide_port_map[outer_port.name]:
                    if inner_port.port_interface_ref == outer_port.port_interface_ref:
                        self._create_delegation_connector_internal(inner_component, inner_port, outer_port)
        for outer_port in sorted(self.require_ports, key=lambda x: x.name):
            if outer_port.name and outer_port.name in inner_require_port_map:
                for inner_component, inner_port in inner_require_port_map[outer_port.name]:
                    if inner_port.port_interface_ref == outer_port.port_interface_ref:
                        self._create_delegation_connector_internal(inner_component, inner_port, outer_port)

    def find_unconnected_ports(self):
        """
        Returns a list unconnected ports found in this composition
        """
        ws = self.root_ws()
        assert (ws is not None)
        unconnected = []
        inner_require_port_map, inner_provide_port_map = self._build_inner_port_map(ws)
        for name in sorted(inner_provide_port_map.keys()):
            for inner_component, provide_port in inner_provide_port_map[name]:
                if self._is_unconnected_port_inner(ws, provide_port):
                    unconnected.append(provide_port)
        for name in sorted(inner_require_port_map.keys()):
            for inner_component, require_port in inner_require_port_map[name]:
                if self._is_unconnected_port_inner(ws, require_port):
                    unconnected.append(require_port)
        all_ports = [*sorted(self.provide_ports, key=lambda x: x.name), *sorted(self.require_ports, key=lambda x: x.name)]
        for port in all_ports:
            if self._is_unconnected_port_outer(ws, port):
                unconnected.append(port)
        return unconnected

    def _is_unconnected_port_inner(self, ws, inner_port: Port):
        inner_port_ref = inner_port.ref
        port_interface = ws.find(inner_port.port_interface_ref)
        if port_interface is None:
            raise ValueError(f'Invalid reference: {inner_port.port_interface_ref}')
        if not isinstance(port_interface, SenderReceiverInterface):
            return False
        for connector in self.assembly_connectors:
            if (connector.provider_instance_ref.port_ref == inner_port_ref) or (connector.requester_instance_ref.port_ref == inner_port_ref):
                return False
        for connector in self.delegation_connectors:
            if connector.inner_port_instance_ref.port_ref == inner_port_ref:
                return False
        return True

    def _is_unconnected_port_outer(self, ws, outer_port: Port):
        outer_port_ref = outer_port.ref
        port_interface = ws.find(outer_port.port_interface_ref)
        if port_interface is None:
            raise ValueError(f'Invalid reference: {outer_port.port_interface_ref}')
        if not isinstance(port_interface, SenderReceiverInterface):
            return False
        for connector in self.delegation_connectors:
            if connector.outer_port_ref.port_ref == outer_port_ref:
                return False
        return True

    def find_mapped_data_type_ref(self, application_data_type_ref: str):
        """
        Returns a reference to the mapped implementation data type or None if not in map
        """
        ws = self.root_ws()
        assert (ws is not None)
        already_processed = set()
        for mapping_ref in self.data_type_mapping_refs:
            if mapping_ref in already_processed:
                continue
            else:
                already_processed.add(mapping_ref)
                mapping_set = ws.find(mapping_ref)
                if mapping_set is None:
                    raise InvalidMappingRef()
                type_ref = mapping_set.find_mapped_data_type_ref(application_data_type_ref)
                if type_ref is not None:
                    return type_ref
        return None


class ComponentPrototype(Element):
    parent: CompositionComponent

    @staticmethod
    def tag(version: float | None = None):
        if version is not None and version >= 4.0:
            return 'SW-COMPONENT-PROTOTYPE'
        return 'COMPONENT-PROTOTYPE'

    def __init__(self, name: str, type_ref: str, parent: CompositionComponent | None = None):
        super().__init__(name, parent)
        self.type_ref = type_ref


class ProviderInstanceRef:
    """
    <PROVIDER-IREF>
    """

    @staticmethod
    def tag(*_):
        return 'PROVIDER-IREF'

    def __init__(self, component_ref: str, port_ref: str):
        self.component_ref = component_ref
        self.port_ref = port_ref

    def asdict(self):
        return {'type': self.__class__.__name__, 'componentRef': self.component_ref, 'portRef': self.port_ref}


class RequesterInstanceRef:
    """
    <REQUESTER-IREF>
    """

    @staticmethod
    def tag(*_):
        return 'REQUESTER-IREF'

    def __init__(self, component_ref: str, port_ref: str):
        self.component_ref = component_ref
        self.port_ref = port_ref

    def asdict(self):
        return {'type': self.__class__.__name__, 'componentRef': self.component_ref, 'portRef': self.port_ref}


class InnerPortInstanceRef:
    """
    <INNER-PORT-IREF>
    """

    @staticmethod
    def tag(*_):
        return 'INNER-PORT-IREF'

    def __init__(self, component_ref: str, port_ref: str):
        self.component_ref = component_ref
        self.port_ref = port_ref

    def asdict(self):
        return {'type': self.__class__.__name__, 'componentRef': self.component_ref, 'portRef': self.port_ref}


class OuterPortRef:
    """
    <OUTER-PORT-REF>
    """

    @staticmethod
    def tag(*_):
        return 'OUTER-PORT-REF'

    def __init__(self, port_ref: str):
        self.port_ref = port_ref

    def asdict(self):
        return {'type': self.__class__.__name__, 'portRef': self.port_ref}


class AssemblyConnector(Element):
    """
    <ASSEMBLY-CONNECTOR-PROTOTYPE>
    """

    @staticmethod
    def tag(version: float | None = None):
        if version is not None and version >= 4.0:
            return 'ASSEMBLY-SW-CONNECTOR'
        return 'ASSEMBLY-CONNECTOR-PROTOTYPE'

    def __init__(
            self,
            name: str,
            provider_instance_ref: ProviderInstanceRef,
            requester_instance_ref: RequesterInstanceRef,
            parent: ArObject | None = None,
    ):
        assert (isinstance(provider_instance_ref, ProviderInstanceRef))
        assert (isinstance(requester_instance_ref, RequesterInstanceRef))
        super().__init__(name, parent)
        self.provider_instance_ref = provider_instance_ref
        self.requester_instance_ref = requester_instance_ref

    def asdict(self):
        return {'type': self.__class__.__name__, 'providerInstanceRef': self.provider_instance_ref.asdict(), 'requesterInstanceRef': self.requester_instance_ref.asdict()}


class DelegationConnector(Element):
    """
    <DELEGATION-CONNECTOR-PROTOTYPE>
    """

    @staticmethod
    def tag(version: float | None = None):
        if version is not None and version >= 4.0:
            return 'DELEGATION-SW-CONNECTOR'
        return 'DELEGATION-CONNECTOR-PROTOTYPE'

    def __init__(
            self,
            name: str,
            inner_port_instance_ref: InnerPortInstanceRef,
            outer_port_ref: OuterPortRef,
            parent: ArObject | None = None,
    ):
        assert (isinstance(inner_port_instance_ref, InnerPortInstanceRef))
        assert (isinstance(outer_port_ref, OuterPortRef))
        super().__init__(name, parent)
        self.inner_port_instance_ref = inner_port_instance_ref
        self.outer_port_ref = outer_port_ref

    def asdict(self):
        return {'type': self.__class__.__name__, 'innerPortInstanceRef': self.inner_port_instance_ref.asdict()}
