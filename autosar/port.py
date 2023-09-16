from __future__ import annotations

"""
Python autosar Ports and ComSpec classes.

Copyright (c) 2019-2021 Conny Gustafsson.
See LICENSE file for additional information.
"""
import copy
from typing import Mapping, Iterable, TYPE_CHECKING

from autosar.ar_object import ArObject
from autosar.base import AdminData, InvalidInitValueRef, InvalidDataTypeRef
from autosar.builder import ValueBuilder
from autosar.constant import Constant, Value, ValueAR4
from autosar.element import Element
from autosar.portinterface import (
    PortInterface,
    ClientServerInterface,
    SenderReceiverInterface,
    NvDataInterface,
    ParameterInterface,
    ModeSwitchInterface,
)

if TYPE_CHECKING:
    from autosar.component import ComponentType

sender_receiver_com_spec_arguments_ar4 = {'dataElement', 'initValue', 'initValueRef', 'aliveTimeout', 'queueLength'}
sender_receiver_com_spec_arguments_ar3 = {'dataElement', 'canInvalidate', 'initValueRef', 'aliveTimeout', 'queueLength'}
client_server_com_spec_arguments = {'operation', 'queueLength'}
mode_switch_com_spec_arguments = {'enhancedMode', 'supportAsync', 'queueLength', 'modeSwitchAckTimeout', 'modeGroup'}
parameter_com_spec_arguments = {'parameter', 'initValue'}
nv_data_com_spec_arguments = {'nvData', 'initValue', 'initValueRef', 'ramBlockInitValue', 'ramBlockInitValueRef', 'romBlockInitValue', 'romBlockInitValueRef'}
valid_com_spec_arguments_ar4 = set().union(sender_receiver_com_spec_arguments_ar4, client_server_com_spec_arguments,
                                           mode_switch_com_spec_arguments, parameter_com_spec_arguments, nv_data_com_spec_arguments)
valid_com_spec_arguments_ar3 = set().union(sender_receiver_com_spec_arguments_ar3, client_server_com_spec_arguments, parameter_com_spec_arguments)


class Port(Element):
    parent: ComponentType

    def __init__(
            self,
            name: str,
            port_interface_ref: str | None,
            com_spec=None,
            auto_create_com_spec: bool = True,
            parent: ComponentType | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.com_spec: list[ComSpec] = []
        if port_interface_ref is not None and not isinstance(port_interface_ref, str):
            raise ValueError('portInterfaceRef needs to be of type None or str')
        self.port_interface_ref = port_interface_ref
        ws = self.root_ws()
        assert (ws is not None)
        port_interface: PortInterface = ws.find(port_interface_ref)

        if com_spec is None and auto_create_com_spec:
            com_spec = self._create_default_com_spec_list(port_interface)

        if com_spec is not None:
            if isinstance(com_spec, ComSpec):
                self.com_spec.append(com_spec)
            elif isinstance(com_spec, Mapping):
                # Typical usage: port interfaces containing a single data element
                com_spec_obj = self._create_com_spec_from_dict(ws, port_interface, com_spec)
                if com_spec_obj is None:
                    raise ValueError(f'Failed to create comspec from comspec data: {com_spec!r}')
                self.com_spec.append(com_spec_obj)
            elif isinstance(com_spec, Iterable):
                # Typical usage: port interfaces containing a multiple data elements
                for data in com_spec:
                    com_spec_obj = self._create_com_spec_from_dict(ws, port_interface, data)
                    if com_spec_obj is None:
                        raise ValueError(f'Failed to create comspec from comspec data: {data!r}')
                    self.com_spec.append(com_spec_obj)
            else:
                raise NotImplementedError('not supported')

    def _create_com_spec_from_dict(self, ws, port_interface: PortInterface, com_spec: Mapping[str, str]):
        """
        Creates ComSpec object based on generic key-value settings from a dictionary.
        """
        self._validate_com_spec_keys_against_port_interface(com_spec, port_interface)

        if isinstance(port_interface, SenderReceiverInterface):
            data_element_name = None
            raw_init_value = None
            init_value = None
            init_value_ref = None  # initValue and initValueRef are mutually exclusive, you cannot have both defined at the same time
            alive_timeout = 0
            queue_length = None
            can_invalidate = False if isinstance(self, ProvidePort) else None

            if 'dataElement' in com_spec:
                data_element_name = str(com_spec['dataElement'])
            if 'initValue' in com_spec:
                raw_init_value = com_spec['initValue']
            if 'initValueRef' in com_spec:
                init_value_ref = str(com_spec['initValueRef'])
            if 'aliveTimeout' in com_spec:
                alive_timeout = int(com_spec['aliveTimeout'])
            if 'queueLength' in com_spec:
                queue_length = int(com_spec['queueLength'])
            if 'canInvalidate' in com_spec:
                can_invalidate = bool(com_spec['canInvalidate'])
            if (data_element_name is None) and (len(port_interface.data_elements) == 1):
                data_element_name = port_interface.data_elements[0].name
            # verify data_element_name
            data_element = port_interface.find(data_element_name)
            if data_element is None:
                raise ValueError(f'Unknown element "{data_element_name}" of portInterface "{port_interface.name}"')
            # verify compatibility of initValueRef
            if init_value_ref is not None:
                init_value_tmp = ws.find(init_value_ref)
                if init_value_tmp is None:
                    raise InvalidInitValueRef(str(init_value_ref))
                if isinstance(init_value_tmp, Constant):
                    if ws.version < 4.0:
                        # This is a convenience implementation for the user.
                        # For AUTOSAR3, initValueRef needs to point to the value inside the Constant
                        if data_element.type_ref != init_value_tmp.value.type_ref:
                            raise ValueError('Constant value has different type from data element, '
                                             f'expected "{data_element.type_ref}", found "{init_value_tmp.value.type_ref}"')
                        init_value_ref = init_value_tmp.value.ref  # correct the reference to the actual value
                    else:
                        init_value_ref = init_value_tmp.ref
                elif isinstance(init_value_tmp, Value):
                    init_value_ref = init_value_tmp.ref
                else:
                    raise ValueError(f'reference is not a Constant or Value object: "{init_value_ref}"')
            # automatically set default value of queueLength to 1 in case the dataElement is queued
            if isinstance(self, RequirePort) and data_element.is_queued and ((queue_length is None) or queue_length == 0):
                queue_length = 1
            if raw_init_value is not None:
                if isinstance(raw_init_value, Value):
                    init_value = raw_init_value
                elif isinstance(raw_init_value, (int, float, str)):
                    data_type = ws.find(data_element.type_ref)
                    if data_type is None:
                        raise InvalidDataTypeRef(data_element.type_ref)
                    value_builder = ValueBuilder()
                    init_value = value_builder.build_from_data_type(data_type, raw_init_value)
                else:
                    raise ValueError('initValue must be an instance of (autosar.constant.Value, int, float, str)')
            return DataElementComSpec(data_element.name, init_value, init_value_ref, alive_timeout, queue_length, can_invalidate)
        elif isinstance(port_interface, ClientServerInterface):
            operation = com_spec.get('operation', None)
            queue_length = com_spec.get('queueLength', 1)
            if operation is not None:
                return OperationComSpec(operation, queue_length)
        elif isinstance(port_interface, ModeSwitchInterface):
            enhanced_mode = com_spec.get('enhancedMode', ws.profile.mode_switch_enhanced_mode_default)
            support_async = com_spec.get('supportAsync', ws.profile.mode_switch_support_async_default)
            queue_length = com_spec.get('queueLength', None)
            mode_switch_ack_timeout = com_spec.get('modeSwitchAckTimeout', None)
            mode_group_name = com_spec.get('modeGroup', None)
            if mode_group_name is None:
                mode_group_name = port_interface.mode_group.name
            if isinstance(self, RequirePort):
                return ModeSwitchComSpec(mode_group_name, enhanced_mode, support_async, None, None)
            else:
                return ModeSwitchComSpec(mode_group_name, enhanced_mode, None, queue_length, mode_switch_ack_timeout)
        elif isinstance(port_interface, ParameterInterface):
            parameter_name = com_spec.get('parameter', None)
            if (parameter_name is None) and (len(port_interface.parameters) == 1):
                parameter_name = port_interface.parameters[0].name
            init_value = com_spec.get('initValue', None)
            return ParameterComSpec(parameter_name, init_value)
        elif isinstance(port_interface, NvDataInterface):
            nv_data_name = None
            if 'nvData' in com_spec:
                nv_data_name = str(com_spec['nvData'])
            if (nv_data_name is None) and (len(port_interface.nv_data) == 1):
                nv_data_name = port_interface.nv_data[0].name
            # verify nvDataName
            nv_data = port_interface.find(nv_data_name)
            if nv_data is None:
                raise ValueError(f'Unknown element "{nv_data_name}" of portInterface "{port_interface.name}"')

            if isinstance(self, RequirePort):
                raw_init_value = None
                init_value = None
                init_value_ref = None  # initValue and initValueRef are mutually exclusive, you cannot have both defined at the same time

                if 'initValue' in com_spec:
                    raw_init_value = com_spec['initValue']
                if 'initValueRef' in com_spec:
                    init_value_ref = str(com_spec['initValueRef'])
                # verify compatibility of initValueRef
                if init_value_ref is not None:
                    init_value_tmp = ws.find(init_value_ref)
                    if init_value_tmp is None:
                        raise InvalidInitValueRef(str(init_value_ref))
                    if isinstance(init_value_tmp, Constant):
                        init_value_ref = init_value_tmp.ref
                    elif isinstance(init_value_tmp, Value):
                        init_value_ref = init_value_tmp.ref
                    else:
                        raise ValueError(f'reference is not a Constant or Value object: "{init_value_ref}"')

                if raw_init_value is not None:
                    if isinstance(raw_init_value, ValueAR4):
                        init_value = raw_init_value
                    elif isinstance(raw_init_value, (int, float, str)):
                        data_type = ws.find(nv_data.type_ref)
                        if data_type is None:
                            raise InvalidDataTypeRef(nv_data.type_ref)
                        value_builder = ValueBuilder()
                        init_value = value_builder.build_from_data_type(data_type, raw_init_value)
                    else:
                        raise ValueError('initValue must be an instance of (autosar.constant.ValueAR4, int, float, str)')
                return NvRequireComSpec(nv_data.name, init_value, init_value_ref)
            else:
                # Provide com spec.
                raw_ram_block_init_value = None
                ram_block_init_value = None
                ram_block_init_value_ref = None  # ramBlockInitValue and ramBlockInitValueRef are mutually exclusive, you cannot have both defined at the same time
                raw_rom_block_init_value = None
                rom_block_init_value = None
                rom_block_init_value_ref = None  # romBlockInitValue and romBlockInitValueRef are mutually exclusive, you cannot have both defined at the same time
                if 'ramBlockInitValue' in com_spec:
                    raw_ram_block_init_value = com_spec['ramBlockInitValue']
                if 'ramBlockInitValueRef' in com_spec:
                    ram_block_init_value_ref = str(com_spec['ramBlockInitValueRef'])
                if 'romBlockInitValue' in com_spec:
                    raw_rom_block_init_value = com_spec['romBlockInitValue']
                if 'romBlockInitValueRef' in com_spec:
                    rom_block_init_value_ref = str(com_spec['romBlockInitValueRef'])

                # verify compatibility of ramBlockInitValueRef
                if ram_block_init_value_ref is not None:
                    init_value_tmp = ws.find(ram_block_init_value_ref)
                    if init_value_tmp is None:
                        raise InvalidInitValueRef(str(ram_block_init_value_ref))
                    if isinstance(init_value_tmp, Constant):
                        ram_block_init_value_ref = init_value_tmp.ref
                    elif isinstance(init_value_tmp, Value):
                        ram_block_init_value_ref = init_value_tmp.ref
                    else:
                        raise ValueError(f'reference is not a Constant or Value object: "{ram_block_init_value_ref}"')

                # verify compatibility of romBlockInitValueRef
                if rom_block_init_value_ref is not None:
                    init_value_tmp = ws.find(rom_block_init_value_ref)
                    if init_value_tmp is None:
                        raise InvalidInitValueRef(str(rom_block_init_value_ref))
                    if isinstance(init_value_tmp, Constant):
                        rom_block_init_value_ref = init_value_tmp.ref
                    elif isinstance(init_value_tmp, Value):
                        rom_block_init_value_ref = init_value_tmp.ref
                    else:
                        raise ValueError(f'reference is not a Constant or Value object: "{rom_block_init_value_ref}"')

                if raw_ram_block_init_value is not None:
                    if isinstance(raw_ram_block_init_value, ValueAR4):
                        ram_block_init_value = raw_ram_block_init_value
                    elif isinstance(raw_ram_block_init_value, (int, float, str)):
                        data_type = ws.find(nv_data.type_ref)
                        if data_type is None:
                            raise InvalidDataTypeRef(nv_data.type_ref)
                        value_builder = ValueBuilder()
                        ram_block_init_value = value_builder.build_from_data_type(data_type, raw_ram_block_init_value)
                    else:
                        raise ValueError('ramBlockInitValue must be an instance of (autosar.constant.ValueAR4, int, float, str)')

                if raw_rom_block_init_value is not None:
                    if isinstance(raw_rom_block_init_value, ValueAR4):
                        rom_block_init_value = raw_rom_block_init_value
                    elif isinstance(raw_rom_block_init_value, (int, float, str)):
                        data_type = ws.find(nv_data.type_ref)
                        if data_type is None:
                            raise InvalidDataTypeRef(nv_data.type_ref)
                        value_builder = ValueBuilder()
                        rom_block_init_value = value_builder.build_from_data_type(data_type, raw_rom_block_init_value)
                    else:
                        raise ValueError('romBlockInitValue must be an instance of (autosar.constant.ValueAR4, int, float, str)')
                return NvProvideComSpec(nv_data.name, ram_block_init_value, ram_block_init_value_ref, rom_block_init_value, rom_block_init_value_ref)
        else:
            raise NotImplementedError(type(port_interface))
        return None

    def _validate_com_spec_keys_against_port_interface(
            self,
            com_spec: Mapping[str, str],
            port_interface: PortInterface | None,
    ):
        if port_interface is None:
            return
        ws = self.root_ws()
        assert (ws is not None)
        if ws.version <= 4.0:
            valid_arguments = valid_com_spec_arguments_ar3
        else:
            valid_arguments = valid_com_spec_arguments_ar4
        for key in com_spec.keys():
            if key not in valid_arguments:
                raise ValueError(f'Unsupported comspec argument "{key}"')

        if isinstance(port_interface, SenderReceiverInterface):
            if ws.version <= 4.0:
                valid_arguments = sender_receiver_com_spec_arguments_ar3
            else:
                valid_arguments = sender_receiver_com_spec_arguments_ar4
        elif isinstance(port_interface, ClientServerInterface):
            valid_arguments = client_server_com_spec_arguments
        elif isinstance(port_interface, ModeSwitchInterface):
            valid_arguments = mode_switch_com_spec_arguments
        elif isinstance(port_interface, ParameterInterface):
            valid_arguments = parameter_com_spec_arguments
        elif isinstance(port_interface, NvDataInterface):
            valid_arguments = nv_data_com_spec_arguments
        else:
            raise RuntimeError(f'Unsupported port interface: {type(port_interface)}')
        for key in com_spec.keys():
            if key not in valid_arguments:
                raise ValueError(f'Comspec argument "{key}" doesn\'t match interface type {type(port_interface)}')

    @staticmethod
    def _create_default_com_spec_list(port_interface: PortInterface | None):
        if port_interface is None:
            return None
        com_spec_list: list[dict[str, str]] = []
        if isinstance(port_interface, SenderReceiverInterface):
            for data_element in port_interface.data_elements:
                com_spec_list.append({'dataElement': data_element.name})
        elif isinstance(port_interface, ClientServerInterface):
            for operation in port_interface.operations:
                com_spec_list.append({'operation': operation.name})
        elif isinstance(port_interface, ParameterInterface):
            for parameter in port_interface.parameters:
                com_spec_list.append({'parameter': parameter.name})
        elif isinstance(port_interface, NvDataInterface):
            for nvData in port_interface.nv_data:
                com_spec_list.append({'nvData': nvData.name})
        elif isinstance(port_interface, ModeSwitchInterface):
            # TODO: Why are we treating ModeSwitchInterface in a different way from the others?
            mode_group_name = port_interface.mode_group.name
            com_spec_list.append({'modeGroup': mode_group_name, 'enhancedMode': False, 'supportAsync': False})
        return None if len(com_spec_list) == 0 else com_spec_list


class RequirePort(Port):
    @staticmethod
    def tag(*_):
        return "R-PORT-PROTOTYPE"

    def __init__(
            self,
            name: str | Port,
            port_interface_ref: str | None = None,
            com_spec=None,
            auto_create_com_spec: bool = True,
            parent: ComponentType | None = None,
    ):
        if isinstance(name, str):
            # normal constructor
            super().__init__(name, port_interface_ref, com_spec, auto_create_com_spec, parent)
        elif isinstance(name, (RequirePort, ProvidePort)):
            other = name  # alias
            # copy constructor
            super().__init__(other.name, other.port_interface_ref, None, False, parent)
            self.com_spec = copy.deepcopy(other.com_spec)
        else:
            raise NotImplementedError(type(name))

    def copy(self):
        """
        returns a copy of itself
        """
        return RequirePort(self)

    def mirror(self):
        """
        returns a mirrored copy of itself
        """
        return ProvidePort(self)


class ProvidePort(Port):
    @staticmethod
    def tag(*_):
        return "P-PORT-PROTOTYPE"

    def __init__(
            self,
            name: str | Port,
            port_interface_ref: str | None = None,
            com_spec=None,
            auto_create_com_spec: bool = True,
            parent: ComponentType | None = None,
    ):
        if isinstance(name, str):
            # normal constructor
            super().__init__(name, port_interface_ref, com_spec, auto_create_com_spec, parent)
        elif isinstance(name, (RequirePort, ProvidePort)):
            other = name  # alias
            # copy constructor
            super().__init__(other.name, other.port_interface_ref, None, False, parent)
            self.com_spec = copy.deepcopy(other.com_spec)
        else:
            raise NotImplementedError(type(name))

    def copy(self):
        """
        returns a copy of itself
        """
        return ProvidePort(self)

    def mirror(self):
        """
        returns a mirrored copy of itself
        """
        return RequirePort(self)


class ComSpec(ArObject):
    def __init__(self, name: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name


class OperationComSpec(ComSpec):
    def __init__(self, name: str | None = None, queue_length: int = 1):
        super().__init__(name)
        self.queue_length = queue_length


class DataElementComSpec(ComSpec):
    def __init__(
            self,
            name: str | None = None,
            init_value: ValueAR4 | None = None,
            init_value_ref: str | None = None,
            alive_timeout: int | None = None,
            queue_length: int | None = None,
            can_invalidate: bool | None = None,
            use_end_to_end_protection: bool | None = None,
    ):
        super().__init__(name)
        if init_value is not None:
            assert (isinstance(init_value, (Value, ValueAR4)))
        self.init_value = init_value
        self.init_value_ref = str(init_value_ref) if init_value_ref is not None else None
        self._alive_timeout = int(alive_timeout) if alive_timeout is not None else None
        self._queue_length = int(queue_length) if queue_length is not None else None
        self.can_invalidate = bool(can_invalidate) if can_invalidate is not None else None
        self.use_end_to_end_protection = bool(use_end_to_end_protection) if use_end_to_end_protection is not None else None

    @property
    def alive_timeout(self):
        return self._alive_timeout

    @alive_timeout.setter
    def alive_timeout(self, val):
        try:
            self._alive_timeout = int(val)
        except ValueError:
            self._alive_timeout = str(val)

    @property
    def queue_length(self):
        return self._queue_length

    @queue_length.setter
    def queue_length(self, val):
        if val is None:
            self._queue_length = None
        else:
            val = int(val)
            if val > 0:
                self._queue_length = int(val)
            else:
                raise ValueError('queueLength must be None or an int greater than zero')


class ModeSwitchComSpec(ComSpec):
    """
    Implementation of <MODE-SWITCH-SENDER-COM-SPEC> and <MODE-SWITCH-RECEIVER-COM-SPEC>

    Attributes:
    name: Name of the ModeGroup in the associated portInterface (str). This has higher precedence than modeGroupRef.
    enhancedMode: Enables/Disables enhanced mode API (None or bool)
    supportAsync: Enables/Disables support for asynchronous call  (None or bool)
    modeGroupRef: Reference to ModeDeclarationGroup (of the same port interface) (None or str)
    queueLength: Length of call queue on the mode user side (None or int)
    modeSwitchAckTimeout: Timeout (in milliseconds) for acknowledgement of the successful processing of the mode switch request (None or int).
    modeGroupRef: Full mode group reference (None or str). This has lower precendence to name (only used when name is None)
    """

    def __init__(
            self,
            name: str | None = None,
            enhanced_mode: bool | None = None,
            support_async: bool | None = None,
            queue_length: int | None = None,
            mode_switch_ack_timeout: int | None = None,
            mode_group_ref: str | None = None,
    ):
        super().__init__(name)
        self.enhanced_mode = bool(enhanced_mode) if enhanced_mode is not None else None
        self.support_async = bool(support_async) if support_async is not None else None
        self._queue_length = int(queue_length) if queue_length is not None else None
        self._mode_switch_ack_timeout = int(mode_switch_ack_timeout) if mode_switch_ack_timeout is not None else None
        self.mode_group_ref = str(mode_group_ref) if mode_group_ref is not None else None

    @staticmethod
    def tag(_, parent_port):
        if isinstance(parent_port, ProvidePort):
            return "MODE-SWITCH-SENDER-COM-SPEC"
        else:
            return "MODE-SWITCH-RECEIVER-COM-SPEC"

    @property
    def queue_length(self):
        return self._queue_length

    @queue_length.setter
    def queue_length(self, val):
        if val is None:
            self._queue_length = None
        else:
            if val > 0:
                self._queue_length = int(val)
            else:
                raise ValueError('queueLength must be None or an int greater than zero')

    @property
    def mode_switch_ack_timeout(self):
        return self._mode_switch_ack_timeout

    @mode_switch_ack_timeout.setter
    def mode_switch_ack_timeout(self, val):
        if val is None:
            self._mode_switch_ack_timeout = None
        else:
            self._mode_switch_ack_timeout = int(val)


class ParameterComSpec(ComSpec):
    def __init__(self, name: str, init_value: str | None = None):
        super().__init__(name)
        self.init_value = init_value


class NvProvideComSpec(ComSpec):
    """
    Implementation of <NV-PROVIDE-COM-SPEC>

    Attributes:
    name: Name of the NvData in the associated portInterface (str). This has higher precedence than modeGroupRef.
    ramBlockInitValue: Ram block init value.
    ramBlockInitValueRef: Ram block init value reference.
    romBlockInitValue: Rom block init value.
    romBlockInitValueRef: Rom block init value reference.
    variableRef: Full NvData reference (None or str). This has lower precendence to name (only used when name is None)
    """

    def __init__(
            self,
            name: str | None = None,
            ram_block_init_value: ValueAR4 | None = None,
            ram_block_init_value_ref: str | None = None,
            rom_block_init_value: ValueAR4 | None = None,
            rom_block_init_value_ref: str | None = None,
            variable_ref: str | None = None,
    ):
        super().__init__(name)
        self.ram_block_init_value = ram_block_init_value
        self.ram_block_init_value_ref = str(ram_block_init_value_ref) if ram_block_init_value_ref is not None else None
        self.rom_block_init_value = rom_block_init_value
        self.rom_block_init_value_ref = str(rom_block_init_value_ref) if rom_block_init_value_ref is not None else None
        self.variable_ref = str(variable_ref) if variable_ref is not None else None

    @staticmethod
    def tag(*_):
        return "NV-PROVIDE-COM-SPEC"


class NvRequireComSpec(ComSpec):
    """
    Implementation of <NV-REQUIRE-COM-SPEC>

    Attributes:
    name: Name of the NvData in the associated portInterface (str). This has higher precedence than modeGroupRef.
    initValue: Init value.
    initValueRef: Ram block init value reference.
    variableRef: Full NvData reference (None or str). This has lower precendence to name (only used when name is None)
    """

    def __init__(
            self,
            name: str | None = None,
            init_value: ValueAR4 | None = None,
            init_value_ref: str | None = None,
            variable_ref: str | None = None,
    ):
        super().__init__(name)
        self.init_value = init_value
        self.init_value_ref = str(init_value_ref) if init_value_ref is not None else None
        self.variable_ref = str(variable_ref) if variable_ref is not None else None

    @staticmethod
    def tag(*_):
        return "NV-REQUIRE-COM-SPEC"
