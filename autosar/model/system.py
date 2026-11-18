from dataclasses import dataclass
from enum import auto
from typing import Iterable, TypeVar, TypeAlias

from autosar.misc import RawStrEnum
from autosar.model.ar_object import ArObject
from autosar.model.base import Identifiable
from autosar.model.element import Element
from autosar.model.enums import ByteOrderEnum, TlsVersionEnum, MappingDirectionEnum
from autosar.model.instance_ref import (
    ComponentInSystemInstanceRef,
    OperationInSystemInstanceRef,
    VariableDataPrototypeInSystemInstanceRef,
    TriggerInSystemInstanceRef,
)


@dataclass
class TextTableValuePair(ArObject):
    first_value: int | float
    second_value: int | float


@dataclass
class TextTableMapping(ArObject):
    identical_mapping: bool
    mapping_direction: MappingDirectionEnum
    bitfield_text_table_mask_first: int | None = None
    bitfield_text_table_mask_second: int | None = None
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
    array_element_mappings: list[SenderRecArrayElementMapping] | None = None
    sender_to_signal_text_table_mapping: TextTableMapping | None = None
    signal_to_receiver_text_table_mapping: TextTableMapping | None = None


@dataclass
class SenderRecRecordTypeMapping(SenderRecCompositeTypeMapping):
    record_element_mapping: list[SenderRecRecordElementMapping] | None = None


AnySenderRecCompositeTypeMapping = TypeVar('AnySenderRecCompositeTypeMapping', bound=SenderRecCompositeTypeMapping)


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
            return_signal_ref: str,
            client_server_operation_instance_ref: OperationInSystemInstanceRef,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.call_signal_ref = call_signal_ref
        self.return_signal_ref = return_signal_ref
        self.client_server_operation_instance_ref = client_server_operation_instance_ref


class SenderReceiverCompositeElementToSignalMapping(DataMapping):
    def __init__(
            self,
            system_signal_ref: str,
            type_mapping: AnySenderRecCompositeTypeMapping,
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
            type_mapping: AnySenderRecCompositeTypeMapping,
            data_element_instance_ref: VariableDataPrototypeInSystemInstanceRef,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.signal_group_ref = signal_group_ref
        self.type_mapping = type_mapping
        self.data_element_instance_ref = data_element_instance_ref


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


class TlsCryptoCipherSuiteProps(Identifiable):
    def __init__(
            self,
            use: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tcp_ip_tls_use_security_extension_force_encrypt_then_mac = use


@dataclass
class TlsPskIdentity(ArObject):
    psk_identity: str | None = None
    psk_identity_hint: str | None = None


class TlsCryptoCipherSuite(Identifiable):
    def __init__(
            self,
            authentication_ref: str | None = None,
            authentication_key_ref: str | None = None,
            cipher_suite_id: int | None = None,
            cipher_suite_short_label: str | None = None,
            elliptic_curve_refs: Iterable[str] | None = None,
            encryption_ref: str | None = None,
            key_exchange_refs: Iterable[str] | None = None,
            key_exchange_authentication_refs: Iterable[str] | None = None,
            priority: int | None = None,
            props: TlsCryptoCipherSuiteProps | None = None,
            psk_identity: TlsPskIdentity | None = None,
            remote_certificate_ref: str | None = None,
            signature_scheme_refs: Iterable[str] | None = None,
            version: TlsVersionEnum | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        props.parent = self
        self.authentication_ref = authentication_ref
        self.authentication_key_ref = authentication_key_ref
        self.cipher_suite_id = cipher_suite_id
        self.cipher_suite_short_label = cipher_suite_short_label
        self.elliptic_curve_refs = self.eval_children(elliptic_curve_refs)
        self.encryption_ref = encryption_ref
        self.key_exchange_refs = self.eval_children(key_exchange_refs)
        self.key_exchange_authentication_refs = self.eval_children(key_exchange_authentication_refs)
        self.priority = priority
        self.props = props
        self.psk_identity = psk_identity
        self.remote_certificate_ref = remote_certificate_ref
        self.signature_scheme_refs = self.eval_children(signature_scheme_refs)
        self.version = version

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        if self.props is not None:
            yield self.props


class CryptoServiceMapping(Identifiable):
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
            key_exchange_refs: Iterable[str] | None = None,
            use_client_authentication_request: bool | None = None,
            use_security_extension_record_size_limit: bool | None = None,
            tls_cipher_suites: Iterable[TlsCryptoCipherSuite] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.key_exchange_refs = self.eval_children(key_exchange_refs)
        self.use_client_authentication_request = use_client_authentication_request
        self.use_security_extension_record_size_limit = use_security_extension_record_size_limit
        self.tls_cipher_suites = self._set_parent(tls_cipher_suites)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.tls_cipher_suites


AnyCryptoServiceMapping: TypeAlias = SecOcCryptoServiceMapping | TlsCryptoServiceMapping


class SwcToEcuMapping(Element):
    def __init__(
            self,
            ecu_instance_ref: str,
            component_instance_refs: list[ComponentInSystemInstanceRef],
            controlled_hw_element_ref: str | None = None,
            processing_unit_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.ecu_instance_ref = ecu_instance_ref
        self.component_instance_refs = component_instance_refs
        self.controlled_hw_element_ref = controlled_hw_element_ref
        self.processing_unit_ref = processing_unit_ref


class SystemMapping(Identifiable):
    def __init__(
            self,
            crypto_service_mappings: Iterable[AnyCryptoServiceMapping] | None = None,
            data_mappings: Iterable[AnyDataMapping] | None = None,
            sw_mappings: Iterable[SwcToEcuMapping] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.crypto_service_mappings = self._set_parent(crypto_service_mappings)
        self.data_mappings = self.eval_children(data_mappings)
        self.sw_mappings = self._set_parent(sw_mappings)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.crypto_service_mappings
        yield from self.sw_mappings


class RootSwCompositionPrototype(Identifiable):
    def __init__(
            self,
            software_composition_type_ref: str,
            calibration_parameter_value_set_refs: Iterable[str] | None = None,
            flat_map_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.software_composition_type_ref = software_composition_type_ref
        self.calibration_parameter_value_set_refs = calibration_parameter_value_set_refs
        self.flat_map_ref = flat_map_ref


class SystemCategory(RawStrEnum):
    SYSTEM_CONSTRAINTS = auto()
    SYSTEM_DESCRIPTION = auto()
    SYSTEM_EXTRACT = auto()
    ECU_EXTRACT = auto()
    ABSTRACT_SYSTEM_DESCRIPTION = auto()
    ECU_SYSTEM_DESCRIPTION = auto()
    SW_CLUSTER_SYSTEM_DESCRIPTION = auto()
    RPT_SYSTEM = auto()


class System(Element):
    _valid_categories = SystemCategory

    def __init__(
            self,
            client_id_definition_set_refs: Iterable[str] | None = None,
            container_header_byte_order: ByteOrderEnum | None = None,
            ecu_extract_version: str | None = None,
            fibex_element_refs: Iterable[str] | None = None,
            interpolation_routine_mapping_set_refs: Iterable[str] | None = None,
            mappings: Iterable[SystemMapping] | None = None,
            pnc_vector_length: int | None = None,
            pnc_vector_offset: int | None = None,
            root_sw_compositions: Iterable[RootSwCompositionPrototype] | None = None,
            sw_cluster_refs: Iterable[str] | None = None,
            system_com_spec_definition_refs: Iterable[str] | None = None,
            system_version: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.client_id_definition_set_refs = self.eval_children(client_id_definition_set_refs)
        self.container_i_pdu_header_byte_order = container_header_byte_order
        self.ecu_extract_version = ecu_extract_version
        self.fibex_element_refs = self.eval_children(fibex_element_refs)
        self.interpolation_routine_mapping_set_refs = self.eval_children(interpolation_routine_mapping_set_refs)
        self.mappings = self._set_parent(mappings)
        self.pnc_vector_length = pnc_vector_length
        self.pnc_vector_offset = pnc_vector_offset
        self.root_software_compositions = self._set_parent(root_sw_compositions)
        self.sw_cluster_refs = self.eval_children(sw_cluster_refs)
        self.system_com_spec_definition_refs = self.eval_children(system_com_spec_definition_refs)
        self.system_version = system_version

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.mappings
        yield from self.root_software_compositions
