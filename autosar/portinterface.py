from typing import Iterable

import autosar.base
from autosar.ar_object import ArObject
from autosar.base import AdminData
from autosar.element import (Element, DataElement, ParameterDataPrototype)
from autosar.mode import ModeGroup


class InvalidationPolicy:
    valid_values = ['DONT-INVALIDATE', 'EXTERNAL-REPLACEMENT', 'KEEP', 'REPLACE']

    @staticmethod
    def tag(*_):
        return 'INVALIDATION-POLICY'

    def __init__(self, data_element_ref, handle_invalid):
        self.data_element_ref = data_element_ref
        self.handle_invalid = handle_invalid

    @property
    def handle_invalid(self):
        return self._handle_invalid

    @handle_invalid.setter
    def handle_invalid(self, value: str):
        if value not in InvalidationPolicy.valid_values:
            raise ValueError(f'invalid value: {value}')
        self._handle_invalid = value


class PortInterface(Element):
    def __init__(
            self,
            name: str,
            is_service: bool = False,
            service_kind: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.is_service = bool(is_service)
        self.service_kind = service_kind

    def __getitem__(self, key: str):
        if isinstance(key, str):
            return self.find(key)
        else:
            raise ValueError('expected string')


class SenderReceiverInterface(PortInterface):
    @staticmethod
    def tag(*_):
        return 'SENDER-RECEIVER-INTERFACE'

    def __init__(
            self,
            name: str,
            is_service: bool = False,
            service_kind: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, is_service, service_kind, parent, admin_data)
        self.data_elements: list[DataElement] = []
        self.mode_groups: list[ModeGroup] = []  # AUTOSAR3 only
        self.invalidation_policies: list[InvalidationPolicy] = []  # AUTOSAR4 only

    def __iter__(self):
        return iter(self.data_elements)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.name == other.name and self.is_service == other.is_service and \
                    self.admin_data == other.admin_data and len(self.data_elements) == len(other.data_elements):
                if (self.mode_groups is not None) and (other.mode_groups is not None) and len(self.mode_groups) == len(other.mode_groups):
                    for i, elem in enumerate(self.mode_groups):
                        if elem != other.mode_groups[i]:
                            return False
                    return True
                for i, elem in enumerate(self.data_elements):
                    if elem != other.data_elements[i]:
                        return False
        return False

    def __ne__(self, other):
        return not (self == other)

    def dir(self):
        return [x.name for x in self.data_elements]

    def find(self, ref: str, *_):
        ref = ref.partition('/')
        name = ref[0]
        for elem in self.data_elements:
            if elem.name == name:
                return elem
        for elem in self.mode_groups:
            if elem.name == name:
                return elem
        return None

    def append(self, elem: Element):
        """
        Adds child element to this port interface
        """
        if isinstance(elem, DataElement):
            self.data_elements.append(elem)
        elif isinstance(elem, ModeGroup):
            self.mode_groups.append(elem)
        elif isinstance(elem, InvalidationPolicy):
            self.invalidation_policies.append(elem)
        else:
            raise ValueError("expected elem variable to be of type DataElement")
        elem.parent = self


class ParameterInterface(PortInterface):
    @staticmethod
    def tag(version: int | float | None = None):
        if version is not None and version >= 4.0:
            return 'PARAMETER-INTERFACE'
        return 'CALPRM-INTERFACE'

    def __init__(
            self,
            name: str,
            is_service: bool = False,
            service_kind: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, is_service, service_kind, parent, admin_data)
        self.parameters: list[Element] = []

    def find(self, ref: str, *_):
        ref = ref.partition('/')
        name = ref[0]
        for elem in self.parameters:
            if elem.name == name:
                return elem

    def append(self, elem: Element):
        """
        adds elem to the self.parameters list and sets elem.parent to self (the port interface)
        """
        if not isinstance(elem, ParameterDataPrototype):
            raise ValueError("Expected elem variable to be of type ParameterDataPrototype")
        self.parameters.append(elem)
        elem.parent = self


class ClientServerInterface(PortInterface):
    def __init__(
            self,
            name: str,
            is_service: bool = False,
            service_kind: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, is_service, service_kind, parent, admin_data)
        self.operations: list[Operation] = []
        self.application_errors: list[ApplicationError] = []

    @staticmethod
    def tag(*_):
        return 'CLIENT-SERVER-INTERFACE'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.name == other.name and self.admin_data == other.admin_data and len(self.operations) == len(other.operations) and \
                    len(self.application_errors) == len(other.application_errors):
                for i, operation in enumerate(self.operations):
                    if operation != other.operations[i]:
                        return False
                for i, applicationError in enumerate(self.application_errors):
                    if applicationError != other.application_errors[i]:
                        return False
                return True
        return False

    def __ne__(self, other):
        return not (self == other)

    def find(self, ref: str, *_):
        ref = ref.partition('/')
        name = ref[0]
        for elem in self.operations:
            if elem.name == name:
                return elem
        for elem in self.application_errors:
            if elem.name == name:
                return elem
        return None

    def append(self, elem: Element):
        """
        Adds elem to the self.operations or self.applicationErrors lists depending on type
        """
        if isinstance(elem, Operation):
            self.operations.append(elem)
        elif isinstance(elem, ApplicationError):
            self.application_errors.append(elem)
        else:
            raise ValueError(f'invalid type: {type(elem)}')
        elem.parent = self


class Operation(Element):
    parent: ClientServerInterface

    @staticmethod
    def tag(version: int | float | None = None):
        if version is not None and version >= 4.0:
            return 'CLIENT-SERVER-OPERATION'
        return 'OPERATION-PROTOTYPE'

    def __init__(self, name: str, parent: ClientServerInterface | None = None):
        super().__init__(name, parent)
        self.arguments: list[Argument] = []
        self.error_refs: list[str] = []

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.name == other.name and self.admin_data == other.admin_data and len(self.arguments) == len(other.arguments) and \
                    (len(self.error_refs) == len(other.error_refs)):
                for i, argument in enumerate(self.arguments):
                    if argument != other.arguments[i]:
                        return False
                for i, errorRef in enumerate(self.error_refs):
                    if errorRef != other.error_refs[i]:
                        return False
                return True
        return False

    def __ne__(self, other):
        return not (self == other)

    def _create_argument(
            self,
            name: str,
            type_ref: str,
            argument_type: str,
            sw_calibration_access: str | None = None,
            server_argument_impl_policy: str | None = None,
    ):
        ws = self.root_ws()
        assert (ws is not None)
        data_type = ws.find(type_ref)
        if data_type is None:
            raise ValueError(f'invalid name or reference: {type_ref}')
        argument = Argument(
            name,
            data_type.ref,
            argument_type,
            sw_calibration_access,
            server_argument_impl_policy,
            parent=self)
        self.arguments.append(argument)
        return argument

    def create_out_argument(
            self,
            name: str,
            type_ref: str,
            sw_calibration_access: str | None = None,
            server_argument_impl_policy: str | None = None,
    ):
        return self._create_argument(name, type_ref, 'OUT', sw_calibration_access, server_argument_impl_policy)

    def create_in_out_argument(
            self,
            name: str,
            type_ref: str,
            sw_calibration_access: str | None = None,
            server_argument_impl_policy: str | None = None,
    ):
        return self._create_argument(name, type_ref, 'INOUT', sw_calibration_access, server_argument_impl_policy)

    def create_in_argument(
            self,
            name: str,
            type_ref: str,
            sw_calibration_access: str | None = None,
            server_argument_impl_policy: str | None = None,
    ):
        return self._create_argument(name, type_ref, 'IN', sw_calibration_access, server_argument_impl_policy)

    def append(self, elem: Element):
        """
        Adds elem to the self.arguments or self.errorRefs lists depending on type
        """
        if isinstance(elem, Argument):
            self.arguments.append(elem)
        elif isinstance(elem, str):
            self.error_refs.append(elem)
        else:
            raise ValueError(f'invalid type: {type(elem)}')
        elem.parent = self

    @property
    def possible_errors(self):
        return None

    @possible_errors.setter
    def possible_errors(self, values: str | Iterable[str]):
        if self.parent is None:
            raise ValueError('cannot call this method without valid parent object')
        if isinstance(values, str):
            values = [values]

        if isinstance(values, Iterable):
            del self.error_refs[:]
            for name in values:
                found = False
                for error in self.parent.application_errors:
                    if error.name == name:
                        self.error_refs.append(error.ref)
                        found = True
                        break
                if not found:
                    raise ValueError(f'invalid error name: "{name}"')
        else:
            raise ValueError('input argument must be string or iterable')


class Argument(Element):
    @staticmethod
    def tag(version: int | float | None = None):
        if version is not None and version >= 4.0:
            return 'ARGUMENT-DATA-PROTOTYPE'
        return 'ARGUMENT-PROTOTYPE'

    def __init__(
            self,
            name: str,
            type_ref: str,
            direction: str,
            sw_calibration_access: str | None = None,
            server_argument_impl_policy: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.type_ref = type_ref
        self._direction = direction
        self.sw_calibration_access = sw_calibration_access
        self.server_argument_impl_policy = server_argument_impl_policy

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value: str):
        if (value != 'IN') and (value != 'OUT') and (value != 'INOUT'):
            raise ValueError(f'invalid value: {value}')
        self._direction = value

    def __eq__(self, other):
        left_ws = self.root_ws()
        right_ws = other.root_ws()
        assert (left_ws is not None)
        assert (right_ws is not None)
        left_type = left_ws.find(self.type_ref)
        if left_type is None:
            raise autosar.base.InvalidDataTypeRef(self.type_ref)
        right_type = right_ws.find(other.type_ref)
        if right_type is None:
            raise autosar.base.InvalidDataTypeRef(other.type_ref)
        if self.direction != other.direction:
            return False
        if (self.sw_calibration_access is None and other.sw_calibration_access is not None) \
                or (self.sw_calibration_access is not None and other.sw_calibration_access is None):
            return False
        if self.sw_calibration_access is not None and other.sw_calibration_access is not None:
            if self.sw_calibration_access != other.sw_calibration_access:
                return False
        if (self.server_argument_impl_policy is None and other.server_argument_impl_policy is not None) or (
                self.server_argument_impl_policy is not None and other.server_argument_impl_policy is None):
            return False
        if self.server_argument_impl_policy is not None and other.server_argument_impl_policy is not None:
            if self.server_argument_impl_policy != other.server_argument_impl_policy:
                return False
        return left_type == right_type

    def __ne__(self, other):
        return not (self == other)


class ApplicationError(Element):
    def __init__(
            self,
            name: str,
            error_code: int,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.error_code = error_code

    @staticmethod
    def tag(*_):
        return 'APPLICATION-ERROR'

    def asdict(self):
        return {'type': self.__class__.__name__, 'name': self.name, 'errorCode': self.error_code}


class ModeSwitchInterface(PortInterface):
    """
    Implementation of <MODE-SWITCH-INTERFACE> (AUTOSAR 4)
    """

    @staticmethod
    def tag(*_):
        return 'MODE-SWITCH-INTERFACE'

    def __init__(
            self,
            name: str,
            is_service: bool = False,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        """
        Arguments:
        name: <SHORT-NAME> (None or str)
        isService: <IS-SERVICE> (None or bool)
        """
        super().__init__(name, is_service, parent, admin_data)
        self._mode_group = None

    @property
    def mode_group(self) -> ModeGroup | None:
        return self._mode_group

    @mode_group.setter
    def mode_group(self, value: ModeGroup):
        if not isinstance(value, ModeGroup):
            raise ValueError('Value must be of ModeGroup type')
        self._mode_group = value

    def find(self, ref: str, *_):
        ref = ref.partition('/')
        name = ref[0]
        mode_group = self.mode_group
        if mode_group is not None and mode_group.name == name:
            return mode_group
        return None


class NvDataInterface(PortInterface):
    @staticmethod
    def tag(version: int | float | None = None):
        if version is not None and version >= 4.0:
            return 'NV-DATA-INTERFACE'
        raise ValueError("Autosar 3 is not supported")

    def __init__(
            self,
            name: str,
            is_service: bool = False,
            service_kind: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, is_service, service_kind, parent, admin_data)
        self.nv_data: list[DataElement] = []

    def find(self, ref: str, *_):
        ref = ref.partition('/')
        name = ref[0]
        for elem in self.nv_data:
            if elem.name == name:
                return elem

    def append(self, elem: DataElement):
        """
        adds elem to the self.nvDatas list and sets elem.parent to self (the port interface)
        """
        if not isinstance(elem, DataElement):
            raise ValueError('Expected elem variable to be of type DataElement')
        self.nv_data.append(elem)
        elem.parent = self


class Trigger(Element):
    def __init__(self, sw_impl_policy: str | None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sw_impl_policy = sw_impl_policy


class TriggerInterface(PortInterface):
    @staticmethod
    def tag(*_):
        return 'TRIGGER-INTERFACE'

    def __init__(
            self,
            name: str,
            is_service: bool = False,
            service_kind: str | None = None,
            triggers: Iterable[Trigger] | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, is_service, service_kind, parent, admin_data)
        self.triggers = self._set_parent(triggers)
        self._find_sets = [self.triggers]
