from autosar.ar_object import ArObject
from autosar.element import Element


class InstanceRef(ArObject):
    def __init__(
            self,
            context_composition_ref: str,
            context_component_ref: str,
            context_port_ref: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.context_composition_ref = context_composition_ref
        self.context_component_ref = context_component_ref
        self.context_port_ref = context_port_ref


class ClientServerOperationInstanceRef(InstanceRef):
    def __init__(self, target_operation_ref: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_operation_ref = target_operation_ref


class DataElementInstanceRef(InstanceRef):
    def __init__(self, target_data_prototype_ref: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_data_prototype_ref = target_data_prototype_ref


class TriggerInstanceRef(InstanceRef):
    def __init__(self, target_trigger_ref: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_trigger_ref = target_trigger_ref


class DataMapping(ArObject):
    def __init__(self, instance_ref: InstanceRef, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance_ref = instance_ref


class ClientServerToSignalMapping(DataMapping):
    instance_ref: ClientServerOperationInstanceRef

    def __init__(
            self,
            call_signal_ref: str,
            return_signal_ref: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.call_signal_ref = call_signal_ref
        self.return_signal_ref = return_signal_ref


class SenderReceiverToSignalMapping(DataMapping):
    instance_ref: DataElementInstanceRef

    def __init__(
            self,
            system_signal_ref: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.system_signal_ref = system_signal_ref


class TriggerToSignalMapping(DataMapping):
    instance_ref: TriggerInstanceRef

    def __init__(
            self,
            system_signal_ref: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.system_signal_ref = system_signal_ref


class SwMapping(Element):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SystemMapping(Element):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_mappings: list[DataMapping] | None = None
        self.sw_mappings: list[SwMapping] | None = None
        self._find_sets = [self.sw_mappings]


class TypeMapping:
    def __init__(self):
        self.elements: list[SenderRecRecordElementMapping] = []


class SenderReceiverToSignalGroupMapping:
    """
    <SENDER-RECEIVER-TO-SIGNAL-GROUP-MAPPING>
    """

    def __init__(self, data_elem_instance_ref: DataElementInstanceRef, signal_group_ref: str, type_mapping: TypeMapping):
        self.data_elem_instance_ref = data_elem_instance_ref
        self.signal_group_ref = signal_group_ref
        self.type_mapping = type_mapping


class ArrayElementMapping(TypeMapping):
    def __init__(self):
        super().__init__()


class RecordElementMapping(TypeMapping):
    def __init__(self):
        super().__init__()


class SenderRecRecordElementMapping:
    def __init__(self, record_element_ref: str, signal_ref: str):
        self.record_element_ref = record_element_ref
        self.signal_ref = signal_ref


class System(Element):
    def __init__(self, name: str, parent: ArObject | None = None):
        super().__init__(name, parent)
        self.ecu_extract_version: str | None = None
        self.system_version: str | None = None
        self.category: str | None = None
        self.fibex_element_refs: list[str] = []
        self._mappings: list[SystemMapping] = []
        self.software_composition = None
        self.pnc_vector_length: int | None = None
        self.pnc_vector_offset: int | None = None
        self._find_sets = [self._mappings]

    @property
    def mappings(self) -> list[SystemMapping]:
        return self._mappings

    @mappings.setter
    def mappings(self, system_mappings: list[SystemMapping]):
        self._mappings = self._set_parent(system_mappings)

    def asdict(self):
        data = {'type': self.__class__.__name__, 'name': self.name,
                }
        if len(self.fibex_element_refs) > 0:
            data['fibexElementRefs'] = self.fibex_element_refs[:]
        return data
