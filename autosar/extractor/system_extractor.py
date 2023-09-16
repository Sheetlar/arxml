import itertools
from dataclasses import dataclass
from typing import Iterable

from autosar.base import AdminData
from autosar.data_transformation import TransformationTechnology
from autosar.ecu import EcuInstance
from autosar.element import DataElement
from autosar.ethernet_cluster import ApplicationEndpoint, NetworkEndpoint, PduTriggering
from autosar.extractor.common import Event, SomeIpFeature
from autosar.extractor.data_type_extractor import ExtractedDataType
from autosar.has_logger import HasLogger
from autosar.pdu import SoConIPduIdentifier, ISignalIPdu, GeneralPurposeIPdu
from autosar.portinterface import Operation, Trigger
from autosar.service_instance_collection import ServiceInstanceCollectionSet, ProvidedServiceInstance, EventHandler
from autosar.signal import SystemSignal, ISignal
from autosar.some_ip_tp import SomeIpConfig, SomeIpConnection
from autosar.system import System, SenderReceiverToSignalMapping, ClientServerToSignalMapping, TriggerToSignalMapping


@dataclass
class ExtractedSystem:
    system: System
    fibex_elements: tuple
    some_ip_mapping: dict[SomeIpFeature, tuple[str, DataElement, tuple[TransformationTechnology, ...]]]
    ecu_mapping: dict[str, EcuInstance]


class SystemExtractor(HasLogger):
    def __init__(self, system: System, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system = system
        self.ws = self.system.root_ws()
        self._get_fibex_elements()

    def __repr__(self):
        return f'{self.__class__.__name__}(system={self.system!r})'

    def extract(self):
        self._logger.debug(f'Started extraction of System "{self.system.name}"')
        self._get_transport_configs()
        self._get_service_interfaces()
        self._scan_provided_services_instances()
        self._scan_data_mappings()
        self._get_combined_mapping()
        extracted = ExtractedSystem(
            system=self.system,
            fibex_elements=self.fibex_elements,
            some_ip_mapping=self.combined_mapping,
            ecu_mapping=self.source_mapping,
        )
        return extracted

    @classmethod
    def extract_system(cls, system: System):
        extractor = cls(system)
        extracted = extractor.extract()
        return extracted

    def _get_fibex_elements(self):
        self.fibex_elements = tuple(filter(
            lambda x: x is not None,
            map(lambda x: self.ws.find(x), self.system.fibex_element_refs),
        ))

    def _get_transport_configs(self):
        self.transport_configs = tuple(itertools.chain.from_iterable(
            map(lambda x: x.tp_connections, filter(lambda x: isinstance(x, SomeIpConfig), self.fibex_elements))
        ))
        self.transport_mapping = {x.transport_pdu_ref: x for x in self.transport_configs}

    def _get_service_interfaces(self):
        if 'SO_SERVICE_INTERFACE' in self.ws.role_elements:
            self.service_mapping = {
                r: c.long_name
                for c in self.ws.role_elements['SO_SERVICE_INTERFACE']
                for r in c.element_refs
            }
        else:
            self.service_mapping = None

    def _scan_provided_services_instances(self):
        self._logger.debug('Scanning Service Instances')
        collection_sets = filter(lambda x: isinstance(x, ServiceInstanceCollectionSet), self.fibex_elements)
        signal_mapping: dict[str, SomeIpFeature] = {}
        transform_mapping: dict[SomeIpFeature, tuple[TransformationTechnology, ...]] = {}
        source_mapping: dict[str, EcuInstance] = {}
        service_instances: Iterable[ProvidedServiceInstance] = filter(
            lambda i: isinstance(i, ProvidedServiceInstance),
            itertools.chain.from_iterable(map(
                lambda s: s.service_instances,
                collection_sets,
            )),
        )
        for service_instance in service_instances:
            service_id = service_instance.service_identifier
            api_version = service_instance.major_version
            try:
                ecu, addr, port = self._get_ip_port_ecu(service_instance)
                source = f'{addr}:{port}'
                if source not in source_mapping:
                    source_mapping[source] = ecu
            except TypeError:  # Returned None
                pass
            events = self._scan_event_groups(service_instance.event_handlers)
            signal_mapping.update(self.get_signal_mapping(service_id, api_version, events))
            transform_mapping.update(self.get_transform_mapping(service_id, api_version, events))
        self.signal_mapping = signal_mapping
        self.transform_mapping = transform_mapping
        self.source_mapping = source_mapping

    def _get_ip_port_ecu(self, service_instance: ProvidedServiceInstance) -> tuple[EcuInstance, str, int] | None:
        if len(service_instance.local_unicast_addresses) != 1:
            return None
        endpoint_ref = service_instance.local_unicast_addresses[0].application_endpoint_ref
        app_endpoint: ApplicationEndpoint = self.ws.find(endpoint_ref)
        net_endpoint: NetworkEndpoint = self.ws.find(app_endpoint.network_endpoint_ref)
        ecu: EcuInstance = self.ws.find(app_endpoint.parent.connector_ref).parent
        ip_address = net_endpoint.network_endpoint_addresses.ipv4_address
        port_number = app_endpoint.tp_configuration.tp.tp_port.port_number
        return ecu, ip_address, port_number

    def _scan_event_groups(self, handlers: Iterable[EventHandler]) -> list[Event]:
        events = []
        for event_group in handlers:
            refs: Iterable[str] = itertools.chain.from_iterable(map(
                lambda g: g.iter_refs(),
                event_group.pdu_activation_routing_groups,
            ))
            for ref in refs:
                event = self._get_signal_transformations_evt_id(ref)
                if event is not None:
                    events.append(event)
        return events

    def _get_signal_transformations_evt_id(self, pdu_identifier_ref: str) -> Event | None:
        pdu_identifier: SoConIPduIdentifier = self.ws.find(pdu_identifier_ref)
        pdu_triggering: PduTriggering = self.ws.find(pdu_identifier.pdu_triggering_ref)
        i_pdu: ISignalIPdu | GeneralPurposeIPdu = self.ws.find(pdu_triggering.i_signal_ref)
        if isinstance(i_pdu, GeneralPurposeIPdu):
            if pdu_triggering.ref not in self.transport_mapping:
                return None
            transport_config: SomeIpConnection = self.transport_mapping[pdu_triggering.ref]
            pdu_triggering: PduTriggering = self.ws.find(transport_config.tp_sdu_ref)
            i_pdu: ISignalIPdu | GeneralPurposeIPdu = self.ws.find(pdu_triggering.i_signal_ref)
        signal: ISignal = self.ws.find(i_pdu.i_signal_to_pdu_mappings[0].i_signal_ref)
        transformations = tuple(map(self.ws.find, itertools.chain.from_iterable(
            map(lambda x: x.transformer_chain_refs, map(self.ws.find, signal.data_transformation_refs)),
        )))
        system_signal: SystemSignal = self.ws.find(signal.system_signal_ref)
        event_id = pdu_identifier.header_id & 0xffff
        return system_signal, transformations, event_id

    def _scan_data_mappings(self):
        mappings = itertools.chain.from_iterable(
            x.data_mappings
            for x in self.system.mappings
            if x.data_mappings is not None
        )
        data_mapping: dict[str, Operation | DataElement | Trigger] = {}
        for mapping in mappings:
            if isinstance(mapping, SenderReceiverToSignalMapping):
                data_element = self.ws.find(mapping.instance_ref.target_data_prototype_ref)
                data_mapping.update({mapping.system_signal_ref: data_element})
            elif isinstance(mapping, ClientServerToSignalMapping):
                operation = self.ws.find(mapping.instance_ref.target_operation_ref)
                data_mapping.update({
                    mapping.call_signal_ref: operation,
                    mapping.return_signal_ref: operation,
                })
            elif isinstance(mapping, TriggerToSignalMapping):
                trigger = self.ws.find(mapping.instance_ref.target_trigger_ref)
                data_mapping.update({mapping.system_signal_ref: trigger})
        self.data_mapping = data_mapping

    def _get_combined_mapping(self):
        self._logger.debug('Combining extracted mappings')
        # noinspection PyUnboundLocalVariable
        self.combined_mapping = {
            e: (self._get_name_from_data_element(x), y)
            for s, e in self.signal_mapping.items()
            if (isinstance((x := self.data_mapping[s]), DataElement)
                and (y := ExtractedDataType(x, self.transform_mapping[e])).elements is not None)
        }

    def _get_name_from_data_element(self, data_element: DataElement) -> str:
        if data_element.admin_data is not None:
            name = self.service_method_from_admin_data(data_element.admin_data)
            if name is not None:
                return name
        name = self.service_method_from_role_elements(data_element)
        if name is not None:
            return name
        return f'{data_element.parent.name}::{data_element.name}'

    def service_method_from_role_elements(self, data_element: DataElement) -> str | None:
        if self.service_mapping is None:
            return None
        if data_element.ref not in self.service_mapping:
            return None
        service_name = self.service_mapping[data_element.ref]
        return f'{service_name}::{data_element.name}'

    @staticmethod
    def get_signal_mapping(
            service_id: int,
            version: int,
            events: list[Event],
    ) -> dict[str, SomeIpFeature]:
        return {s.ref: (service_id, i, version) for s, t, i in events}

    @staticmethod
    def get_transform_mapping(
            service_id: int,
            version: int,
            events: list[Event],
    ) -> dict[SomeIpFeature, tuple[TransformationTechnology, ...]]:
        return {(service_id, i, version): t for s, t, i in events}

    @staticmethod
    def service_method_from_admin_data(admin_data: AdminData) -> str | None:
        service_name_sd = admin_data.find('SYMPHONY_SOMEIPFEATURE_DATA/Service/Name')
        method_name_sd = admin_data.find('SYMPHONY_SOMEIPFEATURE_DATA/SomeipFeature/Name')
        if service_name_sd is None or method_name_sd is None:
            return None
        return f'{service_name_sd.text}::{method_name_sd.text}'
