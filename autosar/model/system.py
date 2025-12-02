from dataclasses import dataclass
from typing import Iterable, TypeVar

from autosar.model.ar_object import ArObject
from autosar.model.element import Element


class AtpInstanceRef(ArObject):
    pass


class ComponentInSystemInstanceRef(AtpInstanceRef):
    def __init__(
            self,
            target_component_ref: str,
            context_composition_ref: str | None = None,
            context_component_refs: list[str] | None = None,
            base_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if context_component_refs is None:
            context_component_refs = []
        self.target_component_ref = target_component_ref
        self.context_composition_ref = context_composition_ref
        self.context_component_refs = context_component_refs
        self.base_ref = base_ref


class OperationInSystemInstanceRef(AtpInstanceRef):
    def __init__(
            self,
            context_port_ref: str,
            target_operation_ref: str,
            context_composition_ref: str | None = None,
            context_component_refs: list[str] | None = None,
            base_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if context_component_refs is None:
            context_component_refs = []
        self.context_port_ref = context_port_ref
        self.target_operation_ref = target_operation_ref
        self.context_composition_ref = context_composition_ref
        self.context_component_refs = context_component_refs
        self.base_ref = base_ref


class VariableDataPrototypeInSystemInstanceRef(AtpInstanceRef):
    def __init__(
            self,
            context_port_ref: str,
            target_data_prototype_ref: str | None = None,
            context_composition_ref: str | None = None,
            context_component_refs: list[str] | None = None,
            base_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if context_component_refs is None:
            context_component_refs = []
        self.context_port_ref = context_port_ref
        self.target_data_prototype_ref = target_data_prototype_ref
        self.context_composition_ref = context_composition_ref
        self.context_component_refs = context_component_refs
        self.base_ref = base_ref


class TriggerInSystemInstanceRef(AtpInstanceRef):
    def __init__(
            self,
            context_port_ref: str,
            target_trigger_ref: str,
            context_composition_ref: str | None = None,
            context_component_refs: list[str] | None = None,
            base_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if context_component_refs is None:
            context_component_refs = []
        self.context_port_ref = context_port_ref
        self.target_trigger_ref = target_trigger_ref
        self.context_composition_ref = context_composition_ref
        self.context_component_refs = context_component_refs
        self.base_ref = base_ref


@dataclass
class TextTableValuePair(ArObject):
    first_value: int | float | None = None
    second_value: int | float | None = None


@dataclass
class TextTableMapping(ArObject):
    bitfield_text_table_mask_first: int | None = None
    bitfield_text_table_mask_second: int | None = None
    identical_mapping: bool | None = None
    mapping_direction: str | None = None
    value_pairs: list[TextTableValuePair] | None = None


@dataclass
class IndexedArrayElement(ArObject):
    index: int
    application_array_element_ref: str | None = None
    implementation_array_element_ref: str | None = None


@dataclass
class SenderRecArrayElementMapping(ArObject):
    indexed_array_element: IndexedArrayElement
    system_signal_ref: str | None = None
    complex_type_mapping: 'SenderRecCompositeTypeMapping | None' = None


@dataclass
class SenderRecRecordElementMapping(ArObject):
    application_record_element_ref: str | None = None
    implementation_record_element_ref: str | None = None
    system_signal_ref: str | None = None
    complex_type_mapping: 'SenderRecCompositeTypeMapping | None' = None
    sender_to_signal_text_table_mapping: TextTableMapping | None = None
    signal_to_receiver_text_table_mapping: TextTableMapping | None = None


class SenderRecCompositeTypeMapping(ArObject):
    pass


@dataclass
class SenderRecArrayTypeMapping(SenderRecCompositeTypeMapping):
    array_element_mapping: list[SenderRecArrayElementMapping] | None = None
    sender_to_signal_text_table_mapping: TextTableMapping | None = None
    signal_to_receiver_text_table_mapping: TextTableMapping | None = None


@dataclass
class SenderRecRecordTypeMapping(SenderRecCompositeTypeMapping):
    record_element_mapping: list[SenderRecRecordElementMapping] | None = None


class DataMapping(ArObject):
    def __init__(
            self,
            introduction: None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.introduction = introduction


class ClientServerToSignalMapping(DataMapping):
    def __init__(
            self,
            call_signal_ref: str,
            client_server_operation_instance_ref: OperationInSystemInstanceRef,
            return_signal_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.call_signal_ref = call_signal_ref
        self.client_server_operation_instance_ref = client_server_operation_instance_ref
        self.return_signal_ref = return_signal_ref


class SenderReceiverCompositeElementToSignalMapping(DataMapping):
    def __init__(
            self,
            system_signal_ref: str,
            type_mapping: SenderRecCompositeTypeMapping,
            data_element_instance_ref: VariableDataPrototypeInSystemInstanceRef | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.system_signal_ref = system_signal_ref
        self.type_mapping = type_mapping
        self.data_element_instance_ref = data_element_instance_ref


class SenderReceiverToSignalGroupMapping(DataMapping):
    def __init__(
            self,
            signal_group_ref: str,
            data_element_instance_ref: VariableDataPrototypeInSystemInstanceRef,
            type_mapping: SenderRecCompositeTypeMapping,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.signal_group_ref = signal_group_ref
        self.data_element_instance_ref = data_element_instance_ref
        self.type_mapping = type_mapping


class SenderReceiverToSignalMapping(DataMapping):
    def __init__(
            self,
            system_signal_ref: str,
            data_element_instance_ref: VariableDataPrototypeInSystemInstanceRef,
            sender_to_signal_text_table_mapping: TextTableMapping | None = None,
            signal_to_receiver_text_table_mapping: TextTableMapping | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.system_signal_ref = system_signal_ref
        self.data_element_instance_ref = data_element_instance_ref
        self.sender_to_signal_text_table_mapping = sender_to_signal_text_table_mapping
        self.signal_to_receiver_text_table_mapping = signal_to_receiver_text_table_mapping


class TriggerToSignalMapping(DataMapping):
    def __init__(
            self,
            system_signal_ref: str,
            trigger_instance_ref: TriggerInSystemInstanceRef,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.system_signal_ref = system_signal_ref
        self.trigger_instance_ref = trigger_instance_ref


AnyDataMapping = TypeVar('AnyDataMapping', bound=DataMapping)


class CryptoServiceMapping(Element):
    pass


class SecOcCryptoServiceMapping(CryptoServiceMapping):
    def __init__(
            self,
            authentication_ref: str | None = None,
            crypto_service_key_ref: str | None = None,
            crypto_service_queue_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.authentication_ref = authentication_ref
        self.crypto_service_key_ref = crypto_service_key_ref
        self.crypto_service_queue_ref = crypto_service_queue_ref


class TlsCryptoServiceMapping(CryptoServiceMapping):
    def __init__(
            self,
            key_exchange_ref: str | None = None,
            use_client_authentication_request: bool | None = None,
            use_security_extension_record_size_limit: bool | None = None,
            tls_cipher_suite: None = None,  # TODO: Class to be implemented
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.key_exchange_ref = key_exchange_ref
        self.use_client_authentication_request = use_client_authentication_request
        self.use_security_extension_record_size_limit = use_security_extension_record_size_limit
        self.tls_cipher_suite = tls_cipher_suite


AnyCryptoServiceMapping = TypeVar('AnyCryptoServiceMapping', bound=CryptoServiceMapping)


class SwcToEcuMapping(Element):
    def __init__(
            self,
            ecu_instance_ref: str,
            component_instance_refs: list[ComponentInSystemInstanceRef],
            controlled_hw_element_ref: str | None = None,
            processing_unit: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.ecu_instance_ref = ecu_instance_ref
        self.component_instance_refs = component_instance_refs
        self.controlled_hw_element_ref = controlled_hw_element_ref
        self.processing_unit = processing_unit


class SystemMapping(Element):
    def __init__(
            self,
            crypto_service_mappings: Iterable[AnyCryptoServiceMapping] | None = None,
            data_mappings: list[AnyDataMapping] | None = None,
            sw_mappings: Iterable[SwcToEcuMapping] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if data_mappings is None:
            data_mappings = []
        self.crypto_service_mappings = self._set_parent(crypto_service_mappings)
        self.data_mappings = data_mappings
        self.sw_mappings = self._set_parent(sw_mappings)
        self._find_sets = (self.crypto_service_mappings, self.sw_mappings)


class System(Element):
    def __init__(
            self,
            fibex_element_refs: list[str] | None = None,
            mappings: Iterable[SystemMapping] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.root_ws().systems.append(self)
        if fibex_element_refs is None:
            fibex_element_refs = []
        self.fibex_element_refs: list[str] = fibex_element_refs
        self.mappings = self._set_parent(mappings)
        self.ecu_extract_version: str | None = None
        self.system_version: str | None = None
        self.category: str | None = None
        self.software_composition = None
        self.pnc_vector_length: int | None = None
        self.pnc_vector_offset: int | None = None
        self._find_sets = (self.mappings,)

    def asdict(self):
        data = {'type': self.__class__.__name__, 'name': self.name,
                }
        if len(self.fibex_element_refs) > 0:
            data['fibexElementRefs'] = self.fibex_element_refs[:]
        return data
