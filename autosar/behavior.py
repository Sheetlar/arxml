from __future__ import annotations

import copy
from typing import Iterable

from autosar.ar_object import ArObject
from autosar.base import AdminData
from autosar.base import (
    find_unique_name_in_list,
    split_ref,
    InvalidRunnableRef,
    InvalidDataElementRef,
    InvalidPortRef,
    InvalidPortInterfaceRef,
    InvalidDataTypeRef,
    InvalidInitValueRef,
)
from autosar.builder import ValueBuilder
from autosar.component import NvBlockComponent
from autosar.constant import Constant, Value, ValueAR4
from autosar.element import Element, DataElement
from autosar.mode import ModeDeclarationGroup, ModeGroup
from autosar.port import Port, RequirePort, ProvidePort
from autosar.portinterface import SenderReceiverInterface, ParameterInterface, NvDataInterface, ModeSwitchInterface, ClientServerInterface, Operation


# --------------------------------------- Events --------------------------------------- #
class Event(Element):
    parent: InternalBehaviorCommon

    def __init__(
            self,
            name: str,
            start_on_event_ref: str | None = None,
            parent: InternalBehaviorCommon | None = None,
    ):
        super().__init__(name, parent)
        self.start_on_event_ref = start_on_event_ref
        self.mode_dependency = None  # for AUTOSAR3
        self.disabled_in_modes = None  # for AUTOSAR4


class ModeSwitchEvent(Event):
    def __init__(
            self,
            name: str,
            start_on_event_ref: str | None = None,
            activation_type: str = 'ENTRY',
            parent: InternalBehaviorCommon | None = None,
            version: float = 3.0,
    ):
        super().__init__(name, start_on_event_ref, parent)
        self.mode_inst_ref: ModeInstanceRef | None = None
        if version < 4.0:
            if (activation_type != 'ENTRY') and (activation_type != 'EXIT'):
                raise ValueError('ActivationType argument must be either "ENTRY" or "EXIT"')
        elif version >= 4.0:
            if activation_type == 'ENTRY':
                activation_type = 'ON-ENTRY'
            if activation_type == 'EXIT':
                activation_type = 'ON-EXIT'
            if (activation_type != 'ON-ENTRY') and (activation_type != 'ON-EXIT'):
                raise ValueError('ActivationType argument must be either "ON-ENTRY" or "ON-EXIT"')
        self.activation_type = activation_type

    @staticmethod
    def tag(version: float):
        return 'SWC-MODE-SWITCH-EVENT' if version >= 4.0 else 'MODE-SWITCH-EVENT'


class TimingEvent(Event):
    def __init__(
            self,
            name: str,
            start_on_event_ref: str | None = None,
            period: int | float = 0,
            parent: InternalBehaviorCommon | None = None,
    ):
        super().__init__(name, start_on_event_ref, parent)
        self.period = int(period)

    @staticmethod
    def tag(*_):
        return 'TIMING-EVENT'


class DataReceivedEvent(Event):
    def __init__(
            self,
            name: str,
            start_on_event_ref: str | None = None,
            parent: InternalBehaviorCommon | None = None,
    ):
        super().__init__(name, start_on_event_ref, parent)
        self.data_instance_ref: DataInstanceRef | None = None
        self.sw_data_defs_props = []

    @staticmethod
    def tag(*_):
        return "DATA-RECEIVED-EVENT"


class OperationInvokedEvent(Event):
    def __init__(
            self,
            name: str,
            start_on_event_ref: str | None = None,
            parent: InternalBehaviorCommon | None = None,
    ):
        super().__init__(name, start_on_event_ref, parent)
        self.operation_instance_ref: OperationInstanceRef | None = None
        self.sw_data_defs_props = []

    @staticmethod
    def tag(*_):
        return "OPERATION-INVOKED-EVENT"


class InitEvent(Event):
    def __init__(
            self,
            name: str,
            start_on_event_ref: str | None = None,
            parent: InternalBehaviorCommon | None = None,
    ):
        super().__init__(name, start_on_event_ref, parent)

    @staticmethod
    def tag(*_):
        return 'INIT-EVENT'


class ModeSwitchAckEvent(Event):
    """
    Represents <MODE-SWITCHED-ACK-EVENT> (AUTOSAR 4)
    """

    def __init__(
            self,
            name: str,
            start_on_event_ref: str | None = None,
            event_source_ref: str | None = None,
            parent: InternalBehaviorCommon | None = None,
    ):
        super().__init__(name, start_on_event_ref, parent)
        self.event_source_ref = event_source_ref

    @staticmethod
    def tag(*_):
        return 'MODE-SWITCHED-ACK-EVENT'


# -------------------------------------------------------------------------------------- #


class ModeDependency(object):
    def __init__(self):
        self.mode_instance_refs: list[ModeInstanceRef | ModeDependencyRef] = []

    def asdict(self):
        data = {'type': self.__class__.__name__, 'modeInstanceRefs': []}
        for mode_instance_ref in self.mode_instance_refs:
            data['modeInstanceRefs'].append(mode_instance_ref.asdict())
        if len(data['modeInstanceRefs']) == 0:
            del data['modeInstanceRefs']

    def append(self, item: ModeInstanceRef | ModeDependencyRef):
        if isinstance(item, ModeInstanceRef) or isinstance(item, ModeDependencyRef):
            self.mode_instance_refs.append(item)
        else:
            raise ValueError('invalid type: ' + str(type(item)))


class ModeInstanceRef:
    """
    Implementation of MODE-IREF (AUTOSAR3, AUTOSAR4)
    """

    def __init__(
            self,
            mode_declaration_ref: str,
            mode_declaration_group_prototype_ref: str | None = None,
            require_port_prototype_ref: str | None = None,
    ):
        self.mode_declaration_ref = mode_declaration_ref  # MODE-DECLARATION-REF
        self.mode_declaration_group_prototype_ref = mode_declaration_group_prototype_ref  # MODE-DECLARATION-GROUP-PROTOTYPE-REF
        self.require_port_prototype_ref = require_port_prototype_ref  # R-PORT-PROTOTYPE-REF

    def asdict(self):
        data = {'type': self.__class__.__name__}
        for key, value in self.__dict__.items():
            data[key] = value
        return data

    @staticmethod
    def tag(*_):
        return 'MODE-IREF'


class ModeDependencyRef:
    def __init__(
            self,
            mode_declaration_ref: str,
            mode_declaration_group_prototype_ref: str | None = None,
            require_port_prototype_ref: str | None = None,
    ):
        self.mode_declaration_ref = mode_declaration_ref  # MODE-DECLARATION-REF
        self.mode_declaration_group_prototype_ref = mode_declaration_group_prototype_ref  # MODE-DECLARATION-GROUP-PROTOTYPE-REF
        self.require_port_prototype_ref = require_port_prototype_ref  # R-PORT-PROTOTYPE-REF

    def asdict(self):
        data = {'type': self.__class__.__name__}
        for key, value in self.__dict__.items():
            data[key] = value
        return data

    @staticmethod
    def tag(*_):
        return 'DEPENDENT-ON-MODE-IREF'


class DisabledModeInstanceRef:
    def __init__(
            self,
            mode_declaration_ref: str,
            mode_declaration_group_prototype_ref: str | None = None,
            require_port_prototype_ref: str | None = None,
    ):
        self.mode_declaration_ref = mode_declaration_ref  # MODE-DECLARATION-REF
        self.mode_declaration_group_prototype_ref = mode_declaration_group_prototype_ref  # MODE-DECLARATION-GROUP-PROTOTYPE-REF
        self.require_port_prototype_ref = require_port_prototype_ref  # R-PORT-PROTOTYPE-REF

    def asdict(self):
        data = {'type': self.__class__.__name__}
        for key, value in self.__dict__.items():
            data[key] = value
        return data

    @staticmethod
    def tag(*_):
        return 'DISABLED-MODE-IREF'


class ModeGroupInstanceRef:
    """
    Base class for RequireModeGroupInstanceRef and ProvideModeGroupInstanceRef
    """

    def __init__(self, mode_group_ref: str, parent: ArObject | None = None):
        """
        This is a very sneaky XML element. Depending on where it is used in the XML schema (XSD)
        it needs to use different XML tags. We solve this by looking at the parent object.
        """
        self.mode_group_ref = mode_group_ref
        self.parent = parent


class RequireModeGroupInstanceRef(ModeGroupInstanceRef):
    def __init__(self, require_port_ref: str, mode_group_ref: str):
        super().__init__(mode_group_ref)
        self.require_port_ref = require_port_ref

    def tag(self, version: float):
        if self.parent is None:
            raise RuntimeError("self.parent cannot be None")
        if version >= 4.0:
            if isinstance(self.parent, ModeAccessPoint):
                return 'R-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF'
            else:
                return 'MODE-GROUP-IREF'
        else:
            raise RuntimeError(f'Not supported in v{version:.1f}')


class ProvideModeGroupInstanceRef(ModeGroupInstanceRef):
    def __init__(self, provide_port_ref: str, mode_group_ref: str):
        super().__init__(mode_group_ref)
        self.provide_port_ref = provide_port_ref

    def tag(self, version: float):
        if self.parent is None:
            raise RuntimeError("self.parent cannot be None")
        if version >= 4.0:
            if isinstance(self.parent, ModeAccessPoint):
                return 'P-MODE-GROUP-IN-ATOMIC-SWC-INSTANCE-REF'
            else:
                return 'MODE-GROUP-IREF'
        else:
            raise RuntimeError(f'Not supported in v{version:.1f}')


class PortAPIOption:
    def __init__(self, port_ref: str, take_address: bool = False, indirect_api: bool = False):
        self.port_ref = port_ref
        self.take_address = take_address
        self.indirect_api = indirect_api

    def asdict(self):
        data = {
            'type': self.__class__.__name__,
            'takeAddress': self.take_address,
            'indirectAPI': self.indirect_api,
            'portRef': self.port_ref,
        }
        return data

    @staticmethod
    def tag(*_):
        return "PORT-API-OPTION"


class DataReceivePoint:
    def __init__(
            self,
            port_ref: str,
            data_elem_ref: str | None = None,
            name: str | None = None,
            parent: ArObject | None = None,
    ):
        self.port_ref = port_ref
        self.data_elem_ref = data_elem_ref
        self.name = name
        self.parent = parent

    @staticmethod
    def tag(version: float):
        return "VARIABLE-ACCESS" if version >= 4.0 else "DATA-RECEIVE-POINT"


class DataSendPoint:
    def __init__(
            self,
            port_ref: str,
            data_elem_ref: str | None = None,
            name: str | None = None,
            parent: ArObject | None = None,
    ):
        self.port_ref = port_ref
        self.data_elem_ref = data_elem_ref
        self.name = name
        self.parent = parent

    @staticmethod
    def tag(version: float): return "VARIABLE-ACCESS" if version >= 4.0 else "DATA-SEND-POINT"


class RunnableEntity(Element):
    def __init__(
            self,
            name: str,
            invoke_concurrently: bool = False,
            symbol: str | None = None,
            parent: Element | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.invoke_concurrently = invoke_concurrently
        self.min_start_interval: int | None = None
        if symbol is None:
            symbol = name
        self.symbol = symbol
        self.data_receive_points: list[DataReceivePoint] = []
        self.data_send_points: list[DataSendPoint] = []
        self.server_call_points: list[SyncServerCallPoint] = []
        self.exclusive_area_refs: list[str] = []
        self.mode_access_points: list[ModeAccessPoint] = []  # AUTOSAR4 only
        self.mode_switch_points: list[ModeSwitchPoint] = []  # AUTOSAR4 only
        self.parameter_access_points: list[ParameterAccessPoint] = []  # AUTOSAR4 only

    @staticmethod
    def tag(*_):
        return 'RUNNABLE-ENTITY'

    def find(self, ref: str | None, *args, **kwargs):
        if ref is None:
            return None
        if ref[0] == '/':
            ref = ref[1:]  # removes initial '/' if it exists
        ref = ref.partition('/')
        name = ref[0]
        found_elem = None
        all_iterables = [*self.mode_access_points, *self.mode_switch_points, *self.parameter_access_points]
        for elem in all_iterables:
            if elem.name == name:
                found_elem = elem
                break
        if found_elem is not None:
            if len(ref[2]) > 0:
                return found_elem.find(ref[2])
            else:
                return found_elem
        return None

    def append(self, elem: DataReceivePoint | DataSendPoint):
        if isinstance(elem, DataReceivePoint):
            data_receive_point = self._verify_data_receive_point(copy.copy(elem))
            self.data_receive_points.append(data_receive_point)
            data_receive_point.parent = self
        elif isinstance(elem, DataSendPoint):
            data_send_point = self._verify_data_send_point(copy.copy(elem))
            self.data_send_points.append(data_send_point)
            data_send_point.parent = self
        else:
            raise NotImplementedError(str(type(elem)))

    def _verify_data_receive_point(self, data_receive_point: DataReceivePoint):
        ws = self.root_ws()
        assert (ws is not None)
        assert (data_receive_point.port_ref is not None)
        if isinstance(data_receive_point.port_ref, Port):
            data_receive_point.port_ref = data_receive_point.port_ref.ref
        if isinstance(data_receive_point.port_ref, str):
            port = ws.find(data_receive_point.port_ref)
            if data_receive_point.data_elem_ref is None:
                # default rule: set dataElemRef to ref of first dataElement in the portinterface
                port_interface = ws.find(port.port_interface_ref)
                assert (port_interface is not None)
                if isinstance(port_interface, (SenderReceiverInterface, ParameterInterface)):
                    data_receive_point.data_elem_ref = port_interface.data_elements[0].ref
                else:
                    raise ValueError(f'Invalid interface type: {type(port_interface)}')
            assert (isinstance(data_receive_point.data_elem_ref, str))
            data_element = ws.find(data_receive_point.data_elem_ref)
            if data_receive_point.name is None:
                # default rule: set the name to REC_<port.name>_<dataElement.name>
                data_receive_point.name = f'REC_{port.name}_{data_element.name}'
        else:
            raise ValueError(f'{self.ref}: portRef must be of type string')
        return data_receive_point

    def _verify_data_send_point(self, data_send_point: DataSendPoint):
        ws = self.root_ws()
        assert (ws is not None)
        assert (data_send_point.port_ref is not None)
        if isinstance(data_send_point.port_ref, Port):
            data_send_point.port_ref = data_send_point.port_ref.ref
        if isinstance(data_send_point.port_ref, str):
            port = ws.find(data_send_point.port_ref)
            if data_send_point.data_elem_ref is None:
                # default rule: set dataElemRef to ref of first dataElement in the portinterface
                port_interface = ws.find(port.port_interface_ref)
                assert (port_interface is not None)
                if isinstance(port_interface, (SenderReceiverInterface, ParameterInterface)):
                    data_send_point.data_elem_ref = port_interface.data_elements[0].ref
                else:
                    raise ValueError(f'Invalid interface type: {type(port_interface)}')
            assert (isinstance(data_send_point.data_elem_ref, str))
            data_element = ws.find(data_send_point.data_elem_ref)
            if data_send_point.name is None:
                # default rule: set the name to SEND_<port.name>_<dataElement.name>
                data_send_point.name = f'SEND_{port.name}_{data_element.name}'
        else:
            raise ValueError(f'{self.ref}: portRef must be of type string')
        return data_send_point

    def root_ws(self):
        if self.parent is None:
            return None
        return self.parent.root_ws()

    @property
    def ref(self):
        if self.parent is not None:
            return self.parent.ref + '/%s' % self.name
        else:
            return None


class DataElementInstanceRef:
    """
    <DATA-ELEMENT-IREF>
    Note: This object seems to be identical to an <DATA-IREF>
    Note 2: Observe that there are multiple <DATA-ELEMENT-IREF> definitions in the AUTOSAR XSD (used for different purposes)
    """

    @staticmethod
    def tag(*_):
        return 'DATA-ELEMENT-IREF'

    def __init__(self, port_ref: str, data_elem_ref: str):
        self.port_ref = port_ref
        self.data_elem_ref = data_elem_ref

    def asdict(self):
        data = {'type': self.__class__.__name__, 'portRef': self.port_ref, 'dataElemRef': self.data_elem_ref}
        return data


class DataInstanceRef:
    """
    <DATA-IREF>
    Note: This object seems to be identical to an <DATA-ELEMENT-IREF>
    """

    @staticmethod
    def tag(*_):
        return 'DATA-IREF'

    def __init__(self, port_ref: str, data_elem_ref: str):
        self.port_ref = port_ref
        self.data_elem_ref = data_elem_ref

    def asdict(self):
        data = {'type': self.__class__.__name__, 'portRef': self.port_ref, 'dataElemRef': self.data_elem_ref}
        return data


class OperationInstanceRef:
    """
    <OBJECT-IREF>
    """

    @staticmethod
    def tag(*_):
        return 'OPERATION-IREF'

    def __init__(self, port_ref: str, operation_ref: str):
        self.port_ref = port_ref
        self.operation_ref = operation_ref

    def asdict(self):
        data = {'type': self.__class__.__name__, 'portRef': self.port_ref, 'operationRef': self.operation_ref}
        return data


class PerInstanceMemory(Element):
    """
    AUTOSAR 3 <PER-INSTANCE-MEMORY>
    Note: I don't know why this XML object has both <TYPE> and <TYPE-DEFINITION> where a simple TYPE-TREF should suffice.
    Internally use a typeRef for PerInstanceMemory. We can transform it back to <TYPE> and <TYPE-DEFINITION> when serializing to XML
    """

    def __init__(self, name: str, type_ref: str, parent: ArObject | None = None):
        super().__init__(name, parent)
        self.type_ref = type_ref

    def asdict(self):
        data = {'type': self.__class__.__name__, 'name': self.name, 'typeRef': self.type_ref}
        return data

    @staticmethod
    def tag(*_):
        return 'PER-INSTANCE-MEMORY'


class SwcNvBlockNeeds(ArObject):
    """
    AUTOSAR 3 representation of SWC-NV-BLOCK-NEEDS
    """

    def __init__(
            self,
            name: str,
            number_of_data_sets: int,
            read_only: bool,
            reliability: str,
            resistant_to_changed_sw: bool,
            restore_at_start: bool,
            write_only_once: bool,
            writing_frequency: int | str | None,
            writing_priority: str | None,
            default_block_ref: str | None,
            mirror_block_ref: str | None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.number_of_data_sets = number_of_data_sets
        assert (isinstance(read_only, bool))
        self.read_only = read_only
        self.reliability = reliability
        assert (isinstance(resistant_to_changed_sw, bool))
        self.resistant_to_changed_sw = resistant_to_changed_sw
        assert (isinstance(restore_at_start, bool))
        self.restore_at_start = restore_at_start
        assert (isinstance(write_only_once, bool))
        self.write_only_once = write_only_once
        self.writing_frequency = writing_frequency
        self.writing_priority = writing_priority
        self.default_block_ref = default_block_ref
        self.mirror_block_ref = mirror_block_ref
        self.service_call_ports: list[RoleBasedRPortAssignment] = []

    def asdict(self):
        data = {'type': self.__class__.__name__, 'serviceCallPorts': []}
        for key, value in self.__dict__.items():
            if 'key' == 'serviceCallPorts':
                pass
            else:
                data[key] = value
        if len(data['serviceCallPorts']) == 0:
            del data['serviceCallPorts']
        return data

    @staticmethod
    def tag(*_):
        return 'SWC-NV-BLOCK-NEEDS'


class NvmBlockConfig:
    """
    Represents NVM block config, used inside an NvmBlockNeeds object.
    All options by default is set to None which means "default configuration".
    In practice a None value means that no XML will be generated for that option.
    Option List:
    - numberOfDataSets: None or int
    - numberOfRomBlocks: None or int
    - ramBlockStatusControl: None or str ('NV-RAM-MANAGER', 'API')
    - reliability: None or str('NO-PROTECTION', 'ERROR-DETECTION', 'ERROR-CORRECTION')
    - writingPriority: None or str ('LOW', 'MEDIUM', 'HIGH')
    - writingFrequency: None or int
    - calcRamBlockCrc: None or bool
    - checkStaticBlockId: None or bool
    - readOnly: None or bool
    - resistantToChangedSw: None or bool
    - restoreAtStartup: None or bool
    - storeAtShutdown: None or bool
    - writeVerification: None or bool
    - writeOnlyOnce: None or bool
    - autoValidationAtShutdown: None or bool
    - useCrcCompMechanism: None or bool
    - storeEmergency: None or bool
    - storeImmediate: None or bool
    - storeCyclic: None or bool
    - cyclicWritePeriod: None or float

    """

    def __init__(
            self,
            number_of_data_sets: int | None = None,
            number_of_rom_blocks: int | None = None,
            ram_block_status_control: str | None = None,
            reliability: str | None = None,
            writing_priority: str | None = None,
            writing_frequency: int | None = None,
            calc_ram_block_crc: bool = False,
            check_static_block_id: bool = False,
            read_only: bool = False,
            resistant_to_changed_sw: bool = False,
            restore_at_startup: bool = False,
            store_at_shutdown: bool = False,
            write_verification: bool = False,
            write_only_once: bool = False,
            auto_validation_at_shutdown: bool = False,
            use_crc_comp_mechanism: bool = False,
            store_emergency: bool = False,
            store_immediate: bool = False,
            store_cyclic: bool = False,
            cyclic_write_period: int | float | None = None,
            check_input: bool = True,
    ):
        self.number_of_data_sets = number_of_data_sets
        self.number_of_rom_blocks = number_of_rom_blocks
        self.ram_block_status_control = ram_block_status_control
        self.reliability = reliability
        self.writing_priority = writing_priority
        self.writing_frequency = writing_frequency
        self.calc_ram_block_crc = calc_ram_block_crc
        self.check_static_block_id = check_static_block_id
        self.read_only = read_only
        self.resistant_to_changed_sw = resistant_to_changed_sw
        self.restore_at_startup = restore_at_startup
        self.store_at_shutdown = store_at_shutdown
        self.write_verification = write_verification
        self.write_only_once = write_only_once
        self.auto_validation_at_shutdown = auto_validation_at_shutdown
        self.use_crc_comp_mechanism = use_crc_comp_mechanism
        self.store_emergency = store_emergency
        self.store_immediate = store_immediate
        self.store_cyclic = store_cyclic
        if isinstance(cyclic_write_period, int):
            cyclic_write_period = float(cyclic_write_period)
        self.cyclic_write_period = cyclic_write_period

        if check_input:
            self.check()

    def check(self):
        if not (self.number_of_data_sets is None or isinstance(self.number_of_data_sets, int)):
            raise ValueError('numberOfDataSets is incorrectly formatted (None or int expected)')
        if not (self.number_of_rom_blocks is None or isinstance(self.number_of_rom_blocks, int)):
            raise ValueError('numberOfRomBlocks is incorrectly formatted (None or int expected)')
        if not (self.ram_block_status_control is None or isinstance(self.ram_block_status_control, str)):
            raise ValueError('ramBlockStatusControl is incorrectly formatted (None or str expected)')
        if not (self.reliability is None or isinstance(self.reliability, str)):
            raise ValueError('reliability is incorrectly formatted (None or str expected)')
        if not (self.writing_priority is None or isinstance(self.writing_priority, str)):
            raise ValueError('writingPriority is incorrectly formatted (None or str expected)')
        if not (self.writing_frequency is None or isinstance(self.writing_frequency, int)):
            raise ValueError('writingFrequency is incorrectly formatted (None or int expected)')
        if not (self.calc_ram_block_crc is None or isinstance(self.calc_ram_block_crc, bool)):
            raise ValueError('calcRamBlockCrc is incorrectly formatted (None or bool expected)')
        if not (self.check_static_block_id is None or isinstance(self.check_static_block_id, bool)):
            raise ValueError('checkStaticBlockId is incorrectly formatted (None or bool expected)')
        if not (self.read_only is None or isinstance(self.read_only, bool)):
            raise ValueError('readOnly is incorrectly formatted (None or bool expected)')
        if not (self.resistant_to_changed_sw is None or isinstance(self.resistant_to_changed_sw, bool)):
            raise ValueError('resistantToChangedSw is incorrectly formatted (None or bool expected)')
        if not (self.restore_at_startup is None or isinstance(self.restore_at_startup, bool)):
            raise ValueError('restoreAtStartup is incorrectly formatted (None or bool expected)')
        if not (self.store_at_shutdown is None or isinstance(self.store_at_shutdown, bool)):
            raise ValueError('storeAtShutdown is incorrectly formatted (None or bool expected)')
        if not (self.write_verification is None or isinstance(self.write_verification, bool)):
            raise ValueError('writeVerification is incorrectly formatted (None or bool expected)')
        if not (self.write_only_once is None or isinstance(self.write_only_once, bool)):
            raise ValueError('writeOnlyOnce is incorrectly formatted (None or bool expected)')
        if not (self.auto_validation_at_shutdown is None or isinstance(self.auto_validation_at_shutdown, bool)):
            raise ValueError('autoValidationAtShutdown is incorrectly formatted (None or bool expected)')
        if not (self.use_crc_comp_mechanism is None or isinstance(self.use_crc_comp_mechanism, bool)):
            raise ValueError('useCrcCompMechanism is incorrectly formatted (None or bool expected)')
        if not (self.store_emergency is None or isinstance(self.store_emergency, bool)):
            raise ValueError('storeEmergency is incorrectly formatted (None or bool expected)')
        if not (self.store_immediate is None or isinstance(self.store_immediate, bool)):
            raise ValueError('storeImmediate is incorrectly formatted (None or bool expected)')
        if not (self.store_cyclic is None or isinstance(self.store_cyclic, bool)):
            raise ValueError('storeCyclic is incorrectly formatted (None or bool expected)')
        if not (self.cyclic_write_period is None or isinstance(self.cyclic_write_period, float)):
            raise ValueError('cyclicWritePeriod is incorrectly formatted (None or float expected)')


class NvmBlockNeeds(Element):
    """
    AUTOSAR 4 representation of NV-BLOCK-NEEDS

    second argument to the init function should be an instance of (a previously configured) NvmBlockConfig

    """

    def __init__(
            self,
            name: str,
            block_config: NvmBlockConfig | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        assert (block_config is None or isinstance(block_config, NvmBlockConfig))
        if block_config is None:
            block_config = NvmBlockConfig()  # create a default configuration
        self.cfg = block_config

    @staticmethod
    def tag(*_):
        return 'NV-BLOCK-NEEDS'


class RoleBasedRPortAssignment:
    def __init__(self, port_ref: str, role: str):
        self.port_ref = port_ref
        self.role = role

    def asdict(self):
        data = {'type': self.__class__.__name__}
        for key, value in self.__dict__.items():
            data[key] = value
        return data

    @staticmethod
    def tag(*_):
        return 'ROLE-BASED-R-PORT-ASSIGNMENT'


class CalPrmElemPrototype(Element):
    """
    <CALPRM-ELEMENT-PROTOTYPE>
    """

    def __init__(
            self,
            name: str,
            type_ref: str,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.type_ref = type_ref
        self.sw_data_def_props: list[str] = []

    def asdict(self):
        data = {'type': self.__class__.__name__, 'name': self.name, 'typeRef': self.type_ref, 'swDataDefsProps': []}
        if self.admin_data is not None:
            data['adminData'] = self.admin_data.asdict()
        for elem in self.sw_data_def_props:
            data['swDataDefsProps'].append(elem)
        return data

    @staticmethod
    def tag(*_):
        return 'CALPRM-ELEMENT-PROTOTYPE'


class ExclusiveArea(Element):
    def __init__(self, name: str, parent: ArObject | None = None, admin_data: AdminData | None = None):
        super().__init__(name, parent, admin_data)

    def asdict(self):
        data = {'type': self.__class__.__name__, 'name': self.name}
        return data

    @staticmethod
    def tag(*_):
        return 'EXCLUSIVE-AREA'


class SyncServerCallPoint:
    """
    <SYNCHRONOUS-SERVER-CALL-POINT>
    """

    def __init__(self, name: str, timeout: float = 0.0):
        self.name = name
        self.timeout = timeout
        self.operation_instance_refs: list[OperationInstanceRef] = []

    def asdict(self):
        data = {
            'type': self.__class__.__name__,
            'name': self.name,
            'timeout': self.timeout,
            'operationInstanceRefs': [x.asdict() for x in self.operation_instance_refs],
        }
        if len(data['operationInstanceRefs']) == 0:
            del data['operationInstanceRefs']
        return data


class InternalBehaviorCommon(Element):
    """
    Base class for InternalBehavior (AUTOSAR 3) and SwcInternalBehavior (AUTOSAR 4)
    """

    def __init__(
            self,
            name: str,
            component_ref: str,
            multiple_instance: bool = False,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        if not isinstance(component_ref, str):  # this is a helper, in case the user called the function with obj instead of obj.ref
            if hasattr(component_ref, 'ref'):
                component_ref = component_ref.ref
        if (component_ref is None) or (not isinstance(component_ref, str)):
            raise ValueError('componentRef: invalid reference')
        self.component_ref = component_ref
        self.multiple_instance = multiple_instance
        self.events: list[Event] = []
        self.port_api_options: list[PortAPIOption] = []
        self.auto_create_port_api_options = False
        self.runnables: list[RunnableEntity] = []
        self.exclusive_areas: list[ExclusiveArea] = []
        self.per_instance_memories: list[PerInstanceMemory] = []
        self.swc = None

    def create_port_api_option_defaults(self):
        self.port_api_options = []
        self._init_swc()
        tmp = self.swc.provide_ports + self.swc.require_ports
        for port in sorted(tmp, key=lambda x: x.name.lower()):
            self.port_api_options.append(PortAPIOption(port.ref))

    def _init_swc(self):
        """
        sets up self.swc if not already setup
        """
        if self.swc is None:
            ws = self.root_ws()
            assert (ws is not None)
            self.swc = ws.find(self.component_ref)
        assert (self.swc is not None)

    def find(self, ref: str, *args, **kwargs):
        if ref is None:
            return None
        if ref[0] == '/':
            ref = ref[1:]  # removes initial '/' if it exists
        ref = ref.partition('/')
        name = ref[0]
        found_elem = None
        all_iterables = [*self.per_instance_memories, *self.exclusive_areas, *self.events]
        for elem in all_iterables:
            if elem.name == name:
                found_elem = elem
                break
        if found_elem is not None:
            if len(ref[2]) > 0:
                return found_elem.find(ref[2])
            else:
                return found_elem
        return None

    def create_runnable(
            self,
            name: str,
            port_access: str | list[str] | None = None,
            symbol: str | None = None,
            concurrent: bool = False,
            exclusive_areas: str | Iterable[str] | None = None,
            mode_switch_point: str | list[str] | None = None,
            min_start_interval: int = 0,
            admin_data: AdminData | None = None,
    ):
        """
        Creates a new runnable and appends it to this InternalBehavior instance
        Parameters:
        * name: <SHORT-NAME> (str)
        * portAccess: List of strings containing port names or "port-name/element" where element can be data-element or an operation (list(str))
        * symbol: Optional symbol name (str). Default is to use self.name string
        * concurrent: Enable/Disable if this runnable can run concurrently (bool).
        * exclusiveAreas: List of strings containing which exclusive areas this runnable will access.
          Note: For mode ports you will at best get read access. If you want to set new modes use modeSwitchPoints.
        * modeSwitchPoint: List of strings containing port names that this runnable will explicitly use for setting modes.
        * minStartInterval: Specifies the time in milliseconds by which two consecutive starts of an ExecutableEntity are guaranteed to be separated.
        * adminData: Optional adminData
        """
        runnable = RunnableEntity(name, concurrent, symbol, self, admin_data)
        runnable.min_start_interval = min_start_interval
        self.runnables.append(runnable)
        self._init_swc()
        ws = self.root_ws()
        if port_access is not None:
            if isinstance(port_access, str):
                port_access = [port_access]
            assert (ws is not None)
            for elem in port_access:
                ref = elem.partition('/')
                if len(ref[1]) == 0:
                    # this section is for portAccess where only the port name is mentioned.
                    # This method only works if the port interface has only 1 data element,
                    # i.e. no ambiguity as to what data element is meant
                    port = self.swc.find(ref[0])
                    if port is None:
                        raise ValueError(f'Invalid port reference: {elem}')
                    port_interface = ws.find(port.port_interface_ref)
                    if port_interface is None:
                        raise ValueError(f'Invalid port interface reference: {port.port_interface_ref}')
                    if isinstance(port_interface, (SenderReceiverInterface, NvDataInterface)):
                        if len(port_interface.data_elements) == 0:
                            continue
                        elif len(port_interface.data_elements) == 1:
                            data_elem = port_interface.data_elements[0]
                            self._create_send_receive_point(port, data_elem, runnable)
                        else:
                            raise NotImplementedError('Port interfaces with multiple data elements not supported')
                    elif isinstance(port_interface, ModeSwitchInterface):
                        mode_group = port_interface.mode_group
                        self._create_mode_access_point(port, mode_group, runnable)
                    else:
                        raise NotImplementedError(type(port_interface))
                else:
                    # this section is for portAccess where both port name and dataelement is represented as "portName/dataElementName"
                    port = self.swc.find(ref[0])
                    if port is None:
                        raise ValueError(f'Invalid port reference: {elem}')
                    port_interface = ws.find(port.port_interface_ref)
                    if port_interface is None:
                        raise ValueError(f'Invalid port interface reference: {port.port_interface_ref}')
                    if isinstance(port_interface, (SenderReceiverInterface, NvDataInterface)):
                        data_elem = port_interface.find(ref[2])
                        if data_elem is None:
                            raise ValueError(f'Invalid data element reference: {elem}')
                        self._create_send_receive_point(port, data_elem, runnable)
                    elif isinstance(port_interface, ClientServerInterface):
                        operation = port_interface.find(ref[2])
                        if operation is None:
                            raise ValueError(f'Invalid operation reference: {elem}')
                        self._create_sync_server_call_point(port, operation, runnable)
                    else:
                        raise NotImplementedError(type(port_interface))
        if exclusive_areas is not None:
            if isinstance(exclusive_areas, str):
                exclusive_areas = [exclusive_areas]
            if isinstance(exclusive_areas, Iterable):
                for exclusive_area_name in exclusive_areas:
                    found = False
                    for exclusive_area in self.exclusive_areas:
                        if exclusive_area.name == exclusive_area_name:
                            found = True
                            runnable.exclusive_area_refs.append(exclusive_area.ref)
                            break
                    if not found:
                        raise ValueError(f'Invalid exclusive area name: {exclusive_area_name}')
            else:
                raise ValueError('exclusiveAreas must be either string or list')
        if mode_switch_point is not None:
            if isinstance(mode_switch_point, str):
                mode_switch_point = [mode_switch_point]
            assert (ws is not None)
            for port_name in mode_switch_point:
                port = self.swc.find(port_name)
                if port is None:
                    raise ValueError(f'Invalid port reference: {port_name}')
                port_interface = ws.find(port.port_interface_ref)
                if port_interface is None:
                    raise ValueError(f'Invalid port interface reference: {port.port_interface_ref}')
                if isinstance(port_interface, ModeSwitchInterface):
                    mode_group = port_interface.mode_group
                    self._create_mode_switch_point(port, mode_group, runnable)
                else:
                    raise NotImplementedError(str(type(port_interface)))
        return runnable

    @staticmethod
    def _create_send_receive_point(port: Port, data_element: DataElement, runnable: RunnableEntity):
        """
        internal function that create a DataReceivePoint of the the port is a require port or
        a DataSendPoint if the port is a provide port
        """
        if isinstance(port, RequirePort):
            receive_point = DataReceivePoint(port.ref, data_element.ref, f'REC_{port.name}_{data_element.name}', runnable)
            runnable.data_receive_points.append(receive_point)
        elif isinstance(port, ProvidePort):
            send_point = DataSendPoint(port.ref, data_element.ref, f'SEND_{port.name}_{data_element.name}', runnable)
            runnable.data_send_points.append(send_point)
        else:
            raise ValueError(f'Unexpected type: {type(port)}')

    @staticmethod
    def _create_sync_server_call_point(port: Port, operation: Operation, runnable: RunnableEntity):
        """
        internal function that create a SyncServerCallPoint of the the port is a require port or
        a DataSendPoint if the port is a provide port
        """
        if isinstance(port, RequirePort):
            call_point = SyncServerCallPoint(f'SC_{port.name}_{operation.name}')
            call_point.operation_instance_refs.append(OperationInstanceRef(port.ref, operation.ref))
            runnable.server_call_points.append(call_point)
        else:
            raise ValueError(f'Unexpected type: {type(port)}')

    def _calc_mode_instance_components_for_require_port(self, port_name: str, mode_value: str):
        self._init_swc()
        ws = self.root_ws()
        port = self.swc.find(port_name)
        if port is None:
            raise ValueError(f'{self.swc.name}: Invalid port name: {port_name}')
        if not isinstance(port, RequirePort):
            raise ValueError(f'{self.swc.name}: port must be a require-port: {port_name}')
        port_interface = ws.find(port.port_interface_ref)
        if port_interface is None:
            raise ValueError(f'Invalid port interface reference: {port.port_interface_ref}')
        if isinstance(port_interface, SenderReceiverInterface):
            if (port_interface.mode_groups is None) or (len(port_interface.mode_groups) == 0):
                raise ValueError(f'Port interface {port_interface.name} has no valid mode groups')
            if len(port_interface.mode_groups) > 1:
                raise NotImplementedError('Pport interfaces with only one mode group is currently supported')
            mode_group = port_interface.mode_groups[0]
        elif isinstance(port_interface, ModeSwitchInterface):
            mode_group = port_interface.mode_group
        else:
            raise NotImplementedError(type(port_interface))
        assert (mode_group is not None)
        data_type = ws.find(mode_group.type_ref)
        if data_type is None:
            raise ValueError(f'{mode_group.name} has invalid typeRef: {mode_group.type_ref}')
        assert (isinstance(data_type, ModeDeclarationGroup))
        mode_declaration_group_ref = mode_group.ref
        for mode_declaration in data_type.mode_declarations:
            if mode_declaration.name == mode_value:
                mode_declaration_ref = mode_declaration.ref
                return mode_declaration_ref, mode_declaration_group_ref, port.ref
        raise ValueError(f'"{mode_value}" did not match any of the mode declarations in {data_type.ref}')

    @staticmethod
    def _create_mode_access_point(port, mode_group: ModeGroup, runnable: RunnableEntity):
        if isinstance(port, ProvidePort):
            mode_group_instance_ref = ProvideModeGroupInstanceRef(port.ref, mode_group.ref)
        else:
            assert isinstance(port, RequirePort)
            mode_group_instance_ref = RequireModeGroupInstanceRef(port.ref, mode_group.ref)
        name = None  # TODO: support user-controlled name?
        mode_access_point = ModeAccessPoint(name, mode_group_instance_ref)
        runnable.mode_access_points.append(mode_access_point)

    @staticmethod
    def _create_mode_switch_point(port: Port, mode_group: ModeGroup, runnable: RunnableEntity):
        if isinstance(port, ProvidePort):
            mode_group_instance_ref = ProvideModeGroupInstanceRef(port.ref, mode_group.ref)
        else:
            assert isinstance(port, RequirePort)
            mode_group_instance_ref = RequireModeGroupInstanceRef(port.ref, mode_group.ref)
        base_name = f'SWITCH_{port.name}_{mode_group.name}'
        name = find_unique_name_in_list(runnable.mode_switch_points, base_name)
        mode_switch_point = ModeSwitchPoint(name, mode_group_instance_ref, runnable)
        runnable.mode_switch_points.append(mode_switch_point)

    def create_mode_switch_event(
            self,
            runnable_name: str,
            mode_ref: str,
            activation_type: str = 'ENTRY',
            name: str | None = None,
    ):
        self._init_swc()
        ws = self.root_ws()
        runnable = self.find(runnable_name)
        if runnable is None:
            raise ValueError(f'Invalid runnable name: {runnable_name}')
        assert (isinstance(runnable, RunnableEntity))

        event_name = name
        if event_name is None:
            base_name = f'MST_{runnable.name}'
            event_name = self._find_event_name(base_name)

        result = mode_ref.partition('/')
        if result[1] != '/':
            raise ValueError(f'Invalid modeRef, expected "portName/modeValue", got "{mode_ref}"')
        port_name = result[0]
        mode_value = result[2]
        event = ModeSwitchEvent(event_name, runnable.ref, activation_type, version=ws.version)
        mode_declaration_ref, mode_declaration_group_ref, port_ref = self._calc_mode_instance_components_for_require_port(port_name, mode_value)
        event.mode_inst_ref = ModeInstanceRef(mode_declaration_ref, mode_declaration_group_ref, port_ref)
        assert (isinstance(event.mode_inst_ref, ModeInstanceRef))
        self.events.append(event)
        return event

    def create_timer_event(
            self,
            runnable_name: str,
            period: int | float,
            mode_dependency: Iterable[str] | None = None,
            name: str | None = None,
    ):
        self._init_swc()
        ws = self.root_ws()

        runnable = self.find(runnable_name)
        if runnable is None:
            raise ValueError(f'Invalid runnable name: {runnable_name}')
        assert (isinstance(runnable, RunnableEntity))
        event_name = name
        if event_name is None:
            # try to find a suitable name for the event
            base_name = f'TMT_{runnable.name}'
            event_name = self._find_event_name(base_name)

        event = TimingEvent(event_name, runnable.ref, period, self)

        if mode_dependency is not None:
            self._process_mode_dependency(event, mode_dependency, ws.version)
        self.events.append(event)
        return event

    def create_timing_event(
            self,
            runnable_name: str,
            period: int | float,
            mode_dependency: Iterable[str] | None = None,
            name: str | None = None,
    ):
        """
        alias for createTimerEvent
        """
        return self.create_timer_event(runnable_name, period, mode_dependency, name)

    def create_operation_invoked_event(
            self,
            runnable_name: str,
            operation_ref: str,
            mode_dependency: Iterable[str] | None = None,
            name: str | None = None,
    ):
        """
        creates a new OperationInvokedEvent
        runnableName: name of the runnable to call (runnable must already exist)
        operationRef: string using the format 'portName/operationName'
        name: optional event name, used to override only
        """
        self._init_swc()
        ws = self.root_ws()

        runnable = self.find(runnable_name)
        if runnable is None:
            raise ValueError(f'Invalid runnable name: {runnable_name}')
        assert (isinstance(runnable, RunnableEntity))

        if not isinstance(operation_ref, str):
            raise ValueError('expected operationRef to be string of the format "portName/operationName"')
        parts = split_ref(operation_ref)
        if len(parts) != 2:
            raise ValueError('"Expected operationRef to be string of the format "portName/operationName""')
        port_name, operation_name = parts[0], parts[1]
        event_name = name
        port = self.swc.find(port_name)
        if (port is None) or not isinstance(port, Port):
            raise ValueError(f'Invalid port name: {port_name}')
        port_interface = ws.find(port.port_interface_ref)
        if port_interface is None:
            raise ValueError(f'Invalid reference: {port.port_interface_ref}')
        if not isinstance(port_interface, ClientServerInterface):
            raise ValueError(f'The referenced port "{port.name}" does not have a ClientServerInterface')
        operation = port_interface.find(operation_name)
        if (operation is None) or not isinstance(operation, Operation):
            raise ValueError(f'Invalid operation name: {operation_name}')
        if event_name is None:
            event_name = self._find_event_name(f'OIT_{runnable.name}_{port.name}_{operation.name}')
        event = OperationInvokedEvent(event_name, runnable.ref, self)
        event.operation_instance_ref = OperationInstanceRef(port.ref, operation.ref)

        if mode_dependency is not None:
            self._process_mode_dependency(event, mode_dependency, ws.version)

        self.events.append(event)
        return event

    def create_data_received_event(
            self,
            runnable_name: str,
            data_element_ref: str,
            mode_dependency: Iterable[str] | None = None,
            name: str | None = None,
    ):
        """
        creates a new DataReceivedEvent
        runnableName: name of the runnable to call (runnable must already exist)
        dataElementRef: string using the format 'portName/dataElementName'. Using 'portName' only is also OK as long as the interface only has one element
        name: optional event name, used to override only
        """
        self._init_swc()
        ws = self.root_ws()

        runnable = self.find(runnable_name)
        if runnable is None:
            raise InvalidRunnableRef(runnable_name)
        assert (isinstance(runnable, RunnableEntity))

        if not isinstance(data_element_ref, str):
            raise InvalidDataElementRef('Expected dataElementRef to be string of the format "portName" or "portName/dataElementName"')

        parts = split_ref(data_element_ref)
        if len(parts) == 2:
            port_name, data_element_name = parts[0], parts[1]
        elif len(parts) == 1:
            port_name, data_element_name = parts[0], None
        else:
            raise InvalidDataElementRef('Expected dataElementRef to be string of the format "portName" or "portName/dataElementName"')

        event_name = name
        port = self.swc.find(port_name)
        if (port is None) or not isinstance(port, Port):
            raise InvalidPortRef(port_name)
        port_interface = ws.find(port.port_interface_ref)
        if port_interface is None:
            raise InvalidPortInterfaceRef(f'Invalid reference: {port.port_interface_ref}')
        if isinstance(port_interface, SenderReceiverInterface):
            if data_element_name is None:
                if len(port_interface.data_elements) == 1:
                    data_element = port_interface.data_elements[0]
                elif len(port_interface.data_elements) > 1:
                    raise InvalidDataElementRef('Expected dataElementRef to be string of the format "portName/dataElementName"')
                else:
                    raise InvalidDataElementRef(f'portInterface "{port_interface.name}" has no data elements')
            else:
                data_element = port_interface.find(data_element_name)
                if not isinstance(data_element, DataElement):
                    raise InvalidDataElementRef(data_element_name)
                elif data_element is None:
                    raise InvalidDataElementRef(f'portInterface "{port_interface.name}" has no operation {data_element_name}')
        elif isinstance(port_interface, NvDataInterface):
            if data_element_name is None:
                if len(port_interface.nv_data) == 1:
                    data_element = port_interface.nv_data[0]
                elif len(port_interface.nv_data) > 1:
                    raise InvalidDataElementRef('Expected dataElementRef to be string of the format "portName/dataElementName"')
                else:
                    raise InvalidDataElementRef(f'portInterface "{port_interface.name}" has no nvdata elements')
            else:
                data_element = port_interface.find(data_element_name)
                if not isinstance(data_element, DataElement):
                    raise InvalidDataElementRef(data_element_name)
                elif data_element is None:
                    raise InvalidDataElementRef(f'portInterface "{port_interface.name}" has no nvdata {data_element_name}')
        else:
            raise InvalidPortRef(f'The referenced port "{port.name}" does not have a SenderReceiverInterface or NvDataInterface')
        if event_name is None:
            event_name = self._find_event_name(f'DRT_{runnable.name}_{port.name}_{data_element.name}')
        event = DataReceivedEvent(event_name, runnable.ref, self)
        event.data_instance_ref = DataInstanceRef(port.ref, data_element.ref)

        if mode_dependency is not None:
            self._process_mode_dependency(event, mode_dependency, ws.version)

        self.events.append(event)
        return event

    def _find_event_name(self, base_name: str):
        return find_unique_name_in_list(self.events, base_name)

    def _process_mode_dependency(self, event: Event, mode_dependency_list: Iterable[str], version: float):
        for dependency in list(mode_dependency_list):
            result = dependency.partition('/')
            if result[1] == '/':
                port_name = result[0]
                mode_value = result[2]
                (
                    mode_declaration_ref,
                    mode_declaration_group_prototype_ref,
                    port_ref,
                ) = self._calc_mode_instance_components_for_require_port(port_name, mode_value)
            else:
                raise ValueError(f'Invalid modeRef, expected "portName/modeValue", got "{dependency}"')
            if version >= 4.0:
                if event.disabled_in_modes is None:
                    event.disabled_in_modes = []
                event.disabled_in_modes.append(DisabledModeInstanceRef(mode_declaration_ref, mode_declaration_group_prototype_ref, port_ref))
            else:
                if event.mode_dependency is None:
                    event.mode_dependency = ModeDependency()
                event.mode_dependency.append(ModeDependencyRef(mode_declaration_ref, mode_declaration_group_prototype_ref, port_ref))

    def create_exclusive_area(self, name: str):
        """
        creates a new ExclusiveArea
        """
        self._init_swc()
        exclusive_area = ExclusiveArea(str(name), self)
        self.exclusive_areas.append(exclusive_area)
        return exclusive_area


class InternalBehavior(InternalBehaviorCommon):
    """ InternalBehavior class (AUTOSAR 3)"""

    def __init__(self, name: str, component_ref: str, multiple_instance: bool = False, parent: ArObject | None = None):
        super().__init__(name, component_ref, multiple_instance, parent)

        self.swc_nv_block_needs: list[SwcNvBlockNeeds] = []
        self.shared_cal_params: list[CalPrmElemPrototype] = []

    @staticmethod
    def tag(*_):
        return 'INTERNAL-BEHAVIOR'

    def append(self, elem: RunnableEntity):
        if isinstance(elem, RunnableEntity):
            self.runnables.append(elem)
            elem.parent = self
        else:
            raise NotImplementedError(str(type(elem)))

    def find(self, ref: str | None, *args, **kwargs):
        if ref is None:
            return None
        result = super().find(ref)
        if result is None:
            if ref[0] == '/':
                ref = ref[1:]  # removes initial '/' if it exists
            ref = ref.partition('/')
            name = ref[0]
            for elem in self.shared_cal_params:
                if elem.name == name:
                    return elem
        else:
            return result
        return None

    def __getitem__(self, key):
        return self.find(key)

    def create_per_instance_memory(self, name: str, type_ref: str):
        """
        creates a new PerInstanceMemory object
        name: name of the object (str)
        typeRef: dataType reference (str)
        """
        self._init_swc()
        ws = self.root_ws()
        data_type = ws.find(type_ref)
        if data_type is None:
            raise ValueError('invalid reference: ' + type_ref)
        per_instance_memory = PerInstanceMemory(name, data_type.ref, self)
        self.per_instance_memories.append(per_instance_memory)
        return per_instance_memory

    def create_shared_cal_param(self, name: str, type_ref: str, sw_addr_method_ref: str, admin_data: AdminData | None = None):
        self._init_swc()
        ws = self.root_ws()
        data_type = ws.find(type_ref)
        if data_type is None:
            raise ValueError('invalid reference: ' + type_ref)
        elem = CalPrmElemPrototype(name, data_type.ref, self, admin_data)
        elem.sw_data_def_props.append(sw_addr_method_ref)
        self.shared_cal_params.append(elem)
        return elem

    def create_nvm_block(self, name: str, block_params: dict[str, ...]):
        """
        creates a new SwcNvBlockNeeds object
        name: name of the object (str)
        blockParams: dict containing additional parameters
        """
        self._init_swc()
        number_of_data_sets = int(block_params['numberOfDataSets'])
        read_only = bool(block_params['readOnly'])
        reliability = str(block_params['reliability'])
        resistant_to_changed_sw = bool(block_params['resistantToChangedSW'])
        restore_at_start = bool(block_params['restoreAtStart'])
        write_only_once = bool(block_params['writeOnlyOnce'])
        writing_frequency = str(block_params['writingFrequency'])
        writing_priority = str(block_params['writingPriority'])
        default_block_ref = None
        mirror_block_ref = None
        # defaultBlockRef
        default_block = block_params['defaultBlock']
        if '/' in default_block:
            default_block_ref = default_block  # use as is
        else:
            for shared_cal_param in self.shared_cal_params:
                if shared_cal_param.name == default_block:
                    default_block_ref = shared_cal_param.ref
                    break
        if default_block_ref is None:
            raise ValueError(f'No SharedCalParam found with name: {default_block}')
        # mirrorBlockref
        mirror_block = block_params['mirrorBlock']
        if '/' in mirror_block:
            mirror_block_ref = mirror_block  # use as is
        else:
            for per_instance_memory in self.per_instance_memories:
                if per_instance_memory.name == mirror_block:
                    mirror_block_ref = per_instance_memory.ref
                    break
        if mirror_block_ref is None:
            raise ValueError(f'No PerInstanceMemory found with name: {mirror_block}')
        elem = SwcNvBlockNeeds(
            name,
            number_of_data_sets,
            read_only,
            reliability,
            resistant_to_changed_sw,
            restore_at_start,
            write_only_once,
            writing_frequency,
            writing_priority,
            default_block_ref,
            mirror_block_ref,
        )
        # serviceCallPorts
        if isinstance(block_params['serviceCallPorts'], str):
            service_call_ports = [block_params['serviceCallPorts']]
        else:
            service_call_ports = block_params['serviceCallPorts']
        if isinstance(service_call_ports, Iterable):
            for data in service_call_ports:
                parts = split_ref(data)
                if len(parts) != 2:
                    raise ValueError('serviceCallPorts must be either string or list of string of the format "portName/operationName"')
                port_name, operation_name = parts[0], parts[1]
                port = self.swc.find(port_name)
                if not isinstance(port, Port):
                    raise ValueError(f'"{port_name}" is not a valid port name')
                elem.service_call_ports.append(RoleBasedRPortAssignment(port.ref, operation_name))
        else:
            raise ValueError('serviceCallPorts must be either string or list of string of format the "portName/operationName"')

        self.swc_nv_block_needs.append(elem)
        return elem


class SwcInternalBehavior(InternalBehaviorCommon):
    """
    AUTOSAR 4 Internal Behavior
    """

    def __init__(self, name: str, component_ref: str, multiple_instance: bool = False, parent: ArObject | None = None):
        super().__init__(name, component_ref, multiple_instance, parent)
        self.service_dependencies: list[SwcServiceDependency] = []
        self.parameter_data_prototype: list[ParameterDataPrototype] = []
        self.data_type_mapping_refs: list[str] = []

    @staticmethod
    def tag(*_):
        return "SWC-INTERNAL-BEHAVIOR"

    def find(self, ref: str | None, *args, **kwargs):
        if ref is None:
            return None
        result = super().find(ref)
        if result is None:
            if ref[0] == '/':
                ref = ref[1:]  # removes initial '/' if it exists
            ref = ref.partition('/')
            name = ref[0]
            found_elem = None
            for elem in self.parameter_data_prototype:
                if elem.name == name:
                    found_elem = elem
                    break
            if found_elem is not None:
                if len(ref[2]) > 0:
                    return found_elem.find(ref[2])
                else:
                    return found_elem
        else:
            return result

    def create_per_instance_memory(
            self,
            name: str,
            implementation_type_ref: str,
    ):
        """
        AUTOSAR4: Creates a DataElement object and appends to the internal perInstanceMemories list
        name: name of the object (str)
        implementationTypeRef: dataType reference (str)
        swAddressMethodRef: Software address method reference (str)
        swCalibrationAccess: software calibration access (str)
        """
        self._init_swc()
        ws = self.root_ws()
        data_type = ws.find(implementation_type_ref)
        if data_type is None:
            raise ValueError(f'Invalid reference: {implementation_type_ref}')
        data_element = PerInstanceMemory(name, data_type.ref, parent=self)
        self.per_instance_memories.append(data_element)
        return data_element

    def create_shared_data_parameter(
            self,
            name: str,
            implementation_type_ref: str,
            sw_address_method_ref: str | None = None,
            sw_calibration_access: str | None = None,
            init_value: str | None = None,
    ):
        """
        AUTOSAR4: Creates a ParameterDataPrototype object and appends it to the internal parameterDataPrototype list
        """
        self._init_swc()
        ws = self.root_ws()
        data_type = ws.find(implementation_type_ref)
        if data_type is None:
            raise ValueError(f'Invalid reference: {implementation_type_ref}')
        parameter = ParameterDataPrototype(
            name,
            data_type.ref,
            sw_address_method_ref=sw_address_method_ref,
            sw_calibration_access=sw_calibration_access,
            init_value=init_value,
            parent=self,
        )
        self.parameter_data_prototype.append(parameter)
        return parameter

    def create_nvm_block(
            self,
            name: str,
            port_name: str,
            per_instance_memory_name: str,
            nvm_block_config: NvmBlockConfig | None = None,
            default_value_name: str | None = None,
            per_instance_memory_role: str = 'ramBlock',
            default_value_role: str = 'defaultValue',
            block_admin_data: AdminData | None = None,
    ):
        """
        AUTOSAR 4: Creates a ServiceNeeds object and appends it to the internal serviceDependencies list
        This assumes the service needed is related to NVM
        """
        self._init_swc()
        if nvm_block_config is None:
            nvm_block_config = NvmBlockConfig()
        assert (isinstance(nvm_block_config, NvmBlockConfig))

        nvm_block_needs = NvmBlockNeeds(name, nvm_block_config, admin_data=block_admin_data)
        nvm_block_service_needs = NvmBlockServiceNeeds(name, nvm_block_needs)
        service_dependency = SwcServiceDependency(name, nvm_block_service_needs)

        for port in self.swc.require_ports:
            if port.name == port_name:
                service_dependency.role_based_port_assignments.append(RoleBasedPortAssignment(port.ref))
                break
        else:
            raise ValueError(f'{self.swc.name}: No require port found with name "{port_name}"')

        for pim in self.per_instance_memories:
            if pim.name == per_instance_memory_name:
                service_dependency.role_based_data_assignments.append(
                    RoleBasedDataAssignment(per_instance_memory_role, local_variable_ref=pim.ref))
                break
        else:
            raise ValueError(f'{self.swc.name}: No per-instance-memory found with name "{per_instance_memory_name}"')
        if default_value_name is not None:
            for param in self.parameter_data_prototype:
                if param.name == default_value_name:
                    service_dependency.role_based_data_assignments.append(
                        RoleBasedDataAssignment(default_value_role, local_parameter_ref=param.ref))
                    break
            else:
                raise ValueError(f'{self.swc.name}: No shared data parameter found with name "{default_value_name}"')

        self.service_dependencies.append(service_dependency)
        return service_dependency

    def create_init_event(self, runnable_name: str, mode_dependency: Iterable[str] | None = None, name: str | None = None):
        self._init_swc()
        ws = self.root_ws()

        runnable = self.find(runnable_name)
        if runnable is None:
            raise ValueError(f'Invalid runnable name: {runnable_name}')
        assert (isinstance(runnable, RunnableEntity))

        event_name = name
        if event_name is None:
            base_name = f'IT_{runnable.name}'
            event_name = self._find_event_name(base_name)

        event = InitEvent(event_name, runnable.ref)

        if mode_dependency is not None:
            self._process_mode_dependency(event, mode_dependency, ws.version)
        self.events.append(event)
        return event

    def create_mode_switch_ack_event(
            self,
            runnable_name: str,
            mode_switch_source: str,
            mode_dependency: Iterable[str] | None = None,
    ):
        """
        Creates a new ModeSwitchAckEvent or <MODE-SWITCHED-ACK-EVENT> (AUTOSAR 4)
        Parameters:
        * runnableName: Name of the runnable to trigger on this event (str)
        * modeSwitchSource: Name of the runnable that has the mode switch point. (str)
                            If the source runnable has multiple mode switch points, use the pattern "RunnableName/ModePortName"
                            To select the correct source point.
        * modeDependency: Modes this runnable shall be disabled in (list(str))
        * name: Event name override (str). Default is to create a name automatically.
        """
        self._init_swc()
        ws = self.root_ws()

        trigger_runnable = self.find(runnable_name)
        if trigger_runnable is None:
            raise ValueError(f'Invalid runnable name: {runnable_name}')
        if not isinstance(trigger_runnable, RunnableEntity):
            raise ValueError(f'Element with name {runnable_name} is not a runnable')

        base_name = f'MSAT_{trigger_runnable.name}'
        event_name = find_unique_name_in_list(self.events, base_name)
        ref = mode_switch_source.partition('/')
        source_runnable_name = ref[0]
        source_runnable = self.find(source_runnable_name)
        if source_runnable is None:
            raise ValueError(f'Invalid runnable name: {source_runnable_name}')
        if not isinstance(source_runnable, RunnableEntity):
            raise ValueError(f'Element with name {source_runnable_name} is not a runnable')
        if len(source_runnable.mode_switch_points) == 0:
            raise RuntimeError(f'Runnable {source_runnable.name} must have at least one mode switch point')
        if len(ref[1]) == 0:
            # No '/' delimiter was used. This is OK only when the source runnable has only one modeSwitchPoint (no ambiguity)
            if len(source_runnable.mode_switch_points) > 1:
                raise ValueError('Ambiguous use of modeSwitchSource. Please use pattern "RunnableName/PortName" in modeSwitchSource argument')
            source_mode_switch_point = source_runnable.mode_switch_points[0]
        else:
            # Search through all modeSwitchPoints to find port name that matches second half of the partition split
            mode_port_name = ref[2]
            for elem in source_runnable.mode_switch_points:
                if not isinstance(elem.mode_group_instance_ref, ProvideModeGroupInstanceRef):
                    continue
                # noinspection PyUnresolvedReferences
                port = ws.find(elem.mode_group_instance_ref.provide_port_ref)
                if port is None:
                    # noinspection PyUnresolvedReferences
                    raise InvalidPortRef(elem.mode_group_instance_ref.provide_port_ref)
                if port.name == mode_port_name:
                    source_mode_switch_point = elem
                    break
            else:
                raise ValueError(f'Invalid modeSwitchSource argument "{mode_switch_source}": '
                                 f'Unable to find a ModeSwitchPoint containing the port name in that runnable')
        assert (source_mode_switch_point is not None)
        # Now that we have collected all the pieces we need we can finally create the event
        assert (trigger_runnable.ref is not None) and (source_mode_switch_point.ref is not None)
        event = ModeSwitchAckEvent(event_name, trigger_runnable.ref, source_mode_switch_point.ref)
        if mode_dependency is not None:
            self._process_mode_dependency(event, mode_dependency, ws.version)
        self.events.append(event)
        return event

    def append_data_type_mapping_ref(self, data_type_mapping_ref: str):
        """
        Adds dataTypeMappingRef to the internal dataTypeMappingRefs list
        """
        self.data_type_mapping_refs.append(data_type_mapping_ref)


class VariableAccess(Element):
    def __init__(
            self,
            name: str,
            port_prototype_ref: str,
            target_data_prototype_ref: str,
            parent: ArObject | None = None,
    ):
        super().__init__(name, parent)
        self.port_prototype_ref = port_prototype_ref
        self.target_data_prototype_ref = target_data_prototype_ref

    @staticmethod
    def tag(*_):
        return 'VARIABLE-ACCESS'


class ServiceNeeds(Element):
    """
    Represents <SERVICE-NEEDS> (AUTOSAR 4)
    This is a base class, it is expected that different service needs derive from this class
    """

    def __init__(
            self,
            name: str | None = None,
            nvm_block_needs: NvmBlockNeeds | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.nvm_block_needs = nvm_block_needs

    @staticmethod
    def tag(*_):
        return 'SERVICE-NEEDS'


class NvmBlockServiceNeeds(ServiceNeeds):
    def __init__(
            self,
            name: str,
            nvm_block_needs: NvmBlockNeeds | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        assert (nvm_block_needs is None or isinstance(nvm_block_needs, NvmBlockNeeds))
        self.nvmBlockNeeds = nvm_block_needs


class SwcServiceDependency(Element):
    """
    Represents <SWC-SERVICE-DEPENDENCY> (AUTODSAR 4)
    """

    def __init__(
            self,
            name: str | None = None,
            service_needs: ServiceNeeds | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.role_based_data_assignments: list[RoleBasedDataAssignment] = []
        self.role_based_port_assignments: list[RoleBasedPortAssignment] = []
        self._service_needs = service_needs

    @property
    def service_needs(self):
        return self._service_needs

    @service_needs.setter
    def service_needs(self, elem: ServiceNeeds):
        elem.parent = self
        self._service_needs = elem

    @staticmethod
    def tag(*_):
        return 'SWC-SERVICE-DEPENDENCY'


class RoleBasedDataAssignment:
    """
    Represents <ROLE-BASED-DATA-ASSIGNMENT> (AUTOSAR 4)
    """

    def __init__(
            self,
            role: str,
            local_variable_ref: str | None = None,
            local_parameter_ref: str | LocalParameterRef | None = None,
    ):
        assert (isinstance(role, str))
        assert (local_variable_ref is None or isinstance(local_variable_ref, str))
        assert (local_parameter_ref is None or isinstance(local_parameter_ref, LocalParameterRef) or isinstance(local_parameter_ref, str))
        self.role = role
        self.local_variable_ref = local_variable_ref
        self.local_parameter_ref = local_parameter_ref

    @staticmethod
    def tag(*_):
        return 'ROLE-BASED-DATA-ASSIGNMENT'


class RoleBasedPortAssignment:
    """
    Represents <ROLE-BASED-PORT-ASSIGNMENT> (AUTOSAR 4)
    """

    def __init__(self, port_ref: str, role: str | None = None):
        assert (isinstance(port_ref, str))
        self.portRef = port_ref
        self.role = role

    @staticmethod
    def tag(*_):
        return 'ROLE-BASED-PORT-ASSIGNMENT'


class ParameterDataPrototype(Element):
    """
    Represents <PARAMETER-DATA-PROTOTYPE> (AUTOSAR 4)
    """

    def __init__(
            self,
            name: str,
            type_ref: str,
            sw_address_method_ref: str | None = None,
            sw_calibration_access: str | None = None,
            init_value: str | None = None,
            init_value_ref: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.type_ref = type_ref
        self.sw_address_method_ref = sw_address_method_ref
        self.sw_calibration_access = sw_calibration_access
        self.init_value = init_value
        self.init_value_ref = init_value_ref

    def tag(self, *_):
        return 'PARAMETER-DATA-PROTOTYPE'


class ParameterInstanceRef:
    """
    Represents <AUTOSAR-PARAMETER-IREF> (AUTOSAR 4)
    """

    def __init__(self, port_ref: str, parameter_data_ref: str):
        self.port_ref = port_ref
        self.parameter_data_ref = parameter_data_ref

    @staticmethod
    def tag(*_):
        return 'AUTOSAR-PARAMETER-IREF'


class LocalParameterRef:
    """
    Represents <LOCAL-PARAMETER-REF> (AUTOSAR 4)
    """

    def __init__(self, parameter_data_ref: str):
        self.parameter_data_ref = parameter_data_ref

    @staticmethod
    def tag(*_):
        return 'LOCAL-PARAMETER-REF'


class ParameterAccessPoint(Element):
    """
    Represents <PARAMETER-ACCESS> (AUTOSAR 4)
    """

    def __init__(
            self,
            name: str,
            accessed_parameter: LocalParameterRef | ParameterInstanceRef | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.accessed_parameter = accessed_parameter

    @staticmethod
    def tag(*_):
        return 'PARAMETER-ACCESS'


class ModeAccessPoint:
    """
    Represents <MODE-ACCESS-POINT> (AUTOSAR 4)
    In the XSD this is not a first-class element.
    Therefore we do not inherit from Element but instead allow <SHORT-NAME> only as (optional) identifier
    """

    def __init__(self, name: str | None = None, mode_group_instance_ref: ModeGroupInstanceRef | None = None):
        """
        Arguments:
        * name: <SHORT-NAME> (None or str)
        * modeGroupInstanceRef: <MODE-GROUP-IREF> (None or (class derived from) ModeGroupInstanceRef)
        """
        self.name = name
        self._mode_group_instance_ref = mode_group_instance_ref

    @property
    def mode_group_instance_ref(self):
        return self._mode_group_instance_ref

    @mode_group_instance_ref.setter
    def mode_group_instance_ref(self, value: ModeGroupInstanceRef | None):
        if value is not None:
            if not isinstance(value, ModeGroupInstanceRef):
                raise ValueError("Value must be None or an instance of ModeGroupInstanceRef")
            self._mode_group_instance_ref = value
            value.parent = self
        else:
            self._mode_group_instance_ref = None

    @staticmethod
    def tag(*_):
        return 'MODE-ACCESS-POINT'


class ModeSwitchPoint(Element):
    """
    Represents <MODE-SWITCH-POINT> (AUTOSAR 4)
    """

    def __init__(
            self,
            name: str,
            mode_group_instance_ref: ModeGroupInstanceRef | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self._mode_group_instance_ref = mode_group_instance_ref

    @property
    def mode_group_instance_ref(self):
        return self._mode_group_instance_ref

    @mode_group_instance_ref.setter
    def mode_group_instance_ref(self, value):
        if value is not None:
            if not isinstance(value, ModeGroupInstanceRef):
                raise ValueError('Value must be None or an instance of ModeGroupInstanceRef')
            self._mode_group_instance_ref = value
            value.parent = self
        else:
            self._mode_group_instance_ref = None

    @staticmethod
    def tag(*_):
        return 'MODE-SWITCH-POINT'


# Behavior parts of NvBlockComponent.
def create_nv_block_descriptor(parent: NvBlockComponent, port_access: str, **kwargs):
    """
    Creates a new NvBlockDescriptor object.
    * parent: NvBlockComponent to create descriptor in.
    * portAccess: String containing port names or "port-name/element" where element is Nvdata (str)
    * base_name: override of the default base_name of the object (str).
    """
    descriptor: NvBlockDescriptor | None = None
    nv_data = None
    ws = parent.root_ws()
    assert (ws is not None)
    assert (isinstance(port_access, str))

    admin_data = kwargs.get('admin_data', None)
    base_name = kwargs.get('base_name', None)
    if base_name is None:
        base_name = 'NvBlckDescr'

    ref = port_access.partition('/')
    port = parent.find(ref[0])
    if port is None:
        raise ValueError(f'Invalid port reference: {port_access}')
    port_interface = ws.find(port.port_interface_ref)
    if port_interface is None:
        raise ValueError(f'Invalid port interface reference: {port.port_interface_ref}')

    if isinstance(port_interface, NvDataInterface):
        if len(ref[1]) == 0:
            # this section is for portAccess where only the port name is mentioned.
            # This method only works if the port interface has only 1 data element,
            # i.e. no ambiguity as to what data element is meant
            if len(port_interface.nv_data) == 1:
                nv_data = port_interface.nv_data[0]
                descriptor = NvBlockDescriptor(f'{base_name}_{port.name}_{nv_data.name}', parent, admin_data)
            else:
                raise NotImplementedError('Port interfaces with multiple data elements not supported')
        else:
            # this section is for portAccess where both port name and dataelement is represented as "portName/dataElementName"
            if isinstance(port_interface, NvDataInterface):
                nv_data = port_interface.find(ref[2])
                if nv_data is None:
                    raise ValueError(f'Invalid data element reference: {port_access}')
                descriptor = NvBlockDescriptor(f'{base_name}_{port.name}_{nv_data.name}', parent, admin_data)
    else:
        raise InvalidPortInterfaceRef(type(port_interface))

    if descriptor is not None:
        data_type_mapping_refs = kwargs.get('data_type_mapping_refs', None)
        nvm_block_config = kwargs.get('nvm_block_config', None)
        timing_event_ref = kwargs.get('timing_event_ref', None)
        sw_calibration_access = kwargs.get('sw_calibration_access', None)
        support_dirty_flag = kwargs.get('support_dirty_flag', False)
        ram_block_admin_data = kwargs.get('ram_block_admin_data', None)
        rom_block_admin_data = kwargs.get('rom_block_admin_data', None)
        rom_block_desc = kwargs.get('rom_block_desc', None)
        rom_block_long_name = kwargs.get('rom_block_long_name', None)
        rom_block_init_value_ref = kwargs.get('rom_block_init_value_ref', None)
        raw_rom_block_init_value = kwargs.get('rom_block_init_value', None)
        rom_block_init_value = None

        if nvm_block_config is None or not isinstance(nvm_block_config, NvmBlockConfig):
            raise InvalidDataTypeRef('NvmBlockConfig is missing or is not an autosar.behavior.NvmBlockConfig')

        descriptor.nv_block_needs = NvmBlockNeeds('NvmBlockNeed', nvm_block_config, parent)

        if data_type_mapping_refs is not None:
            if isinstance(data_type_mapping_refs, str):
                data_type_mapping_refs = [data_type_mapping_refs]
            descriptor.data_type_mapping_refs.extend(data_type_mapping_refs)

        if not isinstance(support_dirty_flag, bool):
            raise ValueError(f'support_dirty_flag must be of bool type: {type(support_dirty_flag)}')

        descriptor.support_dirty_flag = support_dirty_flag

        if isinstance(timing_event_ref, str):
            timing_event = parent.behavior.find(timing_event_ref)
            if timing_event is None:
                raise ValueError(f'Invalid data element reference: {timing_event_ref}')
            descriptor.timing_event_ref = timing_event.name

        # verify compatibility of rom_block_init_value_ref
        if rom_block_init_value_ref is not None:
            init_value_tmp = ws.find(rom_block_init_value_ref)
            if init_value_tmp is None:
                raise InvalidInitValueRef(str(rom_block_init_value_ref))
            if isinstance(init_value_tmp, Constant):
                rom_block_init_value_ref = init_value_tmp.ref
            elif isinstance(init_value_tmp, Value):
                rom_block_init_value_ref = init_value_tmp.ref
            else:
                raise ValueError(f'Reference is not a Constant or Value object: "{rom_block_init_value_ref}"')

        if raw_rom_block_init_value is not None:
            if isinstance(raw_rom_block_init_value, ValueAR4):
                rom_block_init_value = raw_rom_block_init_value
            elif isinstance(raw_rom_block_init_value, (int, float, str)):
                data_type = ws.find(nv_data.typeRef)
                if data_type is None:
                    raise InvalidDataTypeRef(nv_data.typeRef)
                value_builder = ValueBuilder()
                rom_block_init_value = value_builder.build_from_data_type(data_type, raw_rom_block_init_value)
            else:
                raise ValueError('rom_block_init_value must be an instance of (autosar.constant.ValueAR4, int, float, str)')

        data_type = ws.find(nv_data.type_ref)
        if data_type is None:
            raise ValueError(f'Invalid reference: {nv_data.type_ref}')
        descriptor.rom_block = NvBlockRomBlock(
            'ParameterDataPt',
            data_type.ref,
            sw_calibration_access=sw_calibration_access,
            init_value=rom_block_init_value,
            init_value_ref=rom_block_init_value_ref,
            parent=descriptor,
            admin_data=rom_block_admin_data,
        )

        if rom_block_desc is not None:
            descriptor.rom_block.desc = rom_block_desc

        if rom_block_long_name is not None:
            descriptor.rom_block.longName = rom_block_long_name

        descriptor.ram_block = NvBlockRamBlock(
            'VariableDataPt',
            data_type.ref,
            parent=descriptor,
            admin_data=ram_block_admin_data,
        )

        nv_block_data_mapping = NvBlockDataMapping(descriptor)
        nv_block_data_mapping.nv_ram_block_element = NvRamBlockElement(
            parent=nv_block_data_mapping,
            local_variable_ref=descriptor.ram_block,
        )

        if isinstance(port, RequirePort):
            nv_block_data_mapping.written_nv_data = WrittenNvData(
                parent=nv_block_data_mapping,
                autosar_variable_port_ref=port,
                autosar_variable_element_ref=nv_data,
            )

        if isinstance(port, ProvidePort):
            nv_block_data_mapping.read_nv_data = ReadNvData(
                parent=nv_block_data_mapping,
                autosar_variable_port_ref=port,
                autosar_variable_element_ref=nv_data,
            )

        descriptor.nv_block_data_mappings.append(nv_block_data_mapping)
        parent.nv_block_descriptors.append(descriptor)
    return descriptor


class NvBlockRamBlock(DataElement):
    """
    <RAM-BLOCK>
    """

    def __init__(
            self,
            name: str,
            type_ref: str,
            is_queued: bool = False,
            sw_address_method_ref: str | None = None,
            sw_calibration_access: str | None = None,
            sw_impl_policy: str | None = None,
            category: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, type_ref, is_queued, sw_address_method_ref, sw_calibration_access, sw_impl_policy, category, parent, admin_data)

    @classmethod
    def cast(cls, ram_block: DataElement):
        """Cast an autosar.element.DataElement into a NvBlockRamBlock."""
        assert isinstance(ram_block, DataElement)
        ram_block.__class__ = cls
        assert isinstance(ram_block, NvBlockRamBlock)
        return ram_block

    @staticmethod
    def tag(*_):
        return 'RAM-BLOCK'


class NvBlockRomBlock(ParameterDataPrototype):
    """
    Represents <ROM-BLOCK>
    """

    def __init__(
            self,
            name: str,
            type_ref: str,
            sw_address_method_ref: str | None = None,
            sw_calibration_access: str | None = None,
            init_value: str | None = None,
            init_value_ref: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(
            name=name,
            parent=parent,
            type_ref=type_ref,
            sw_address_method_ref=sw_address_method_ref,
            sw_calibration_access=sw_calibration_access,
            init_value=init_value,
            init_value_ref=init_value_ref,
            admin_data=admin_data,
        )

    @classmethod
    def cast(cls, rom_block: ParameterDataPrototype):
        """Cast an ParameterDataPrototype into a NvBlockRomBlock."""
        assert isinstance(rom_block, ParameterDataPrototype)
        rom_block.__class__ = cls
        assert isinstance(rom_block, NvBlockRomBlock)
        return rom_block

    @staticmethod
    def tag(*_):
        return 'ROM-BLOCK'


class NvBlockDescriptor(Element):
    """
    <NV-BLOCK-DESCRIPTOR>
    """

    def __init__(self, name: str, parent: ArObject | None = None, admin_data: AdminData | None = None):
        super().__init__(name, parent, admin_data)
        self.data_type_mapping_refs: list[str] = []
        self.nv_block_data_mappings: list[NvBlockDataMapping] = []
        self.nv_block_needs: NvmBlockNeeds | None = None
        self.ram_block: NvBlockRamBlock | None = None
        self.rom_block: NvBlockRomBlock | None = None
        self.support_dirty_flag = False
        self.timing_event_ref: str | None = None

    def find(self, ref: str, *args, **kwargs):
        parts = ref.partition('/')
        for elem in self.ram_block, self.rom_block:
            if elem.name == parts[0]:
                return elem
        return None

    @staticmethod
    def tag(*_):
        return 'NV-BLOCK-DESCRIPTOR'


class NvBlockDataMapping(ArObject):
    """
    <NV-BLOCK-DATA-MAPPING>
    """

    def __init__(self, parent: ArObject | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.nv_ram_block_element: NvRamBlockElement | None = None
        self.read_nv_data: ReadNvData | None = None
        self.written_nv_data: WrittenNvData | None = None
        self.written_read_nv_data: WrittenReadNvData | None = None

    @staticmethod
    def tag(*_):
        return 'NV-BLOCK-DATA-MAPPING'


class AutosarVariableRef(ArObject):
    """
    Base class for type AUTOSAR-VARIABLE-REF
    * localVariableRef: This reference is used if the variable is local to the current component.
    * autosarVariablePortRef: Port part of the autosarVariableRef.
    * autosarVariableElementRef: Element part of the autosarVariableRef.
    """

    @staticmethod
    def tag(*_):
        return "AUTOSAR-VARIABLE-REF"

    def __init__(
            self,
            parent: ArObject | None = None,
            local_variable_ref: any = None,
            autosar_variable_port_ref: any = None,
            autosar_variable_element_ref: any = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.parent = parent

        if isinstance(local_variable_ref, str):
            self.local_variable_ref = local_variable_ref
        elif hasattr(local_variable_ref, 'ref'):
            assert (isinstance(local_variable_ref.ref, str))
            self.local_variable_ref = local_variable_ref.ref
        else:
            self.local_variable_ref = None

        if isinstance(autosar_variable_port_ref, str):
            self.autosar_variable_port_ref = autosar_variable_port_ref
        elif hasattr(autosar_variable_port_ref, 'ref'):
            assert (isinstance(autosar_variable_port_ref.ref, str))
            self.autosar_variable_port_ref = autosar_variable_port_ref.ref
        else:
            self.autosar_variable_port_ref = None

        if isinstance(autosar_variable_element_ref, str):
            self.autosar_variable_element_ref = autosar_variable_element_ref
        elif hasattr(autosar_variable_element_ref, 'ref'):
            assert (isinstance(autosar_variable_element_ref.ref, str))
            self.autosar_variable_element_ref = autosar_variable_element_ref.ref
        else:
            self.autosar_variable_element_ref = None


class NvRamBlockElement(AutosarVariableRef):
    def __init__(self, parent: ArObject | None = None, local_variable_ref: any = None):
        super().__init__(parent=parent, local_variable_ref=local_variable_ref)

    @staticmethod
    def tag(*_):
        return "NV-RAM-BLOCK-ELEMENT"


class ReadNvData(AutosarVariableRef):
    def __init__(
            self,
            parent: ArObject | None = None,
            autosar_variable_port_ref: any = None,
            autosar_variable_element_ref: any = None,
    ):
        super().__init__(
            parent=parent,
            autosar_variable_port_ref=autosar_variable_port_ref,
            autosar_variable_element_ref=autosar_variable_element_ref,
        )

    @staticmethod
    def tag(*_):
        return "READ-NV-DATA"


class WrittenNvData(AutosarVariableRef):
    def __init__(
            self,
            parent: ArObject | None = None,
            autosar_variable_port_ref: any = None,
            autosar_variable_element_ref: any = None,
    ):
        super().__init__(
            parent=parent,
            autosar_variable_port_ref=autosar_variable_port_ref,
            autosar_variable_element_ref=autosar_variable_element_ref,
        )

    @staticmethod
    def tag(*_):
        return "WRITTEN-NV-DATA"


class WrittenReadNvData(AutosarVariableRef):
    def __init__(
            self,
            parent: ArObject | None = None,
            autosar_variable_port_ref: any = None,
            autosar_variable_element_ref: any = None,
    ):
        super().__init__(
            parent=parent,
            autosar_variable_port_ref=autosar_variable_port_ref,
            autosar_variable_element_ref=autosar_variable_element_ref,
        )

    @staticmethod
    def tag(*_):
        return "WRITTEN-READ-NV-DATA"
