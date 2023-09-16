from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.parser.parser_base import ElementParser
from autosar.service_instance_collection import (
    ServiceInstanceCollectionSet,
    ConsumedServiceInstance,
    ConsumedEventGroup,
    ProvidedServiceInstance,
    EventHandler,
    ApplicationEndpointRefConditional,
    PDUActivationRoutingGroup,
)


class ServiceInstanceCollectionParser(ElementParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_supported_tags(self):
        return ['SERVICE-INSTANCE-COLLECTION-SET']

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> ServiceInstanceCollectionSet | None:
        if xml_element.tag == 'SERVICE-INSTANCE-COLLECTION-SET':
            return self._parse_service_instance_collection_set(xml_element, parent)
        return None

    def _parse_service_instance_collection_set(self, xml_elem: Element, parent: ArObject | None) -> ServiceInstanceCollectionSet:
        name = None
        service_instances = None
        for child_element in xml_elem.findall('./*'):
            match child_element.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(child_element)
                case 'SERVICE-INSTANCES':
                    service_instances = self._parse_element_list(
                        child_element,
                        {
                            'PROVIDED-SERVICE-INSTANCE': self._parse_provided_service_instance,
                            'CONSUMED-SERVICE-INSTANCE': self._parse_consumed_service_instance,
                        },
                    )
                case _:
                    self._logger.warning(f'Unexpected tag: {child_element.tag}')
        collection_set = ServiceInstanceCollectionSet(
            name=name,
            service_instances=service_instances,
            parent=parent,
        )
        return collection_set

    def _parse_consumed_service_instance(self, xml_element: Element) -> ConsumedServiceInstance:
        name = None
        major_version = None
        minor_version = None
        instance_identifier = None
        service_identifier = None
        consumed_event_groups = None
        local_unicast_addresses = None
        for elem in xml_element.findall('./*'):
            match elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(elem)
                case 'MAJOR-VERSION':
                    major_version = self.parse_int_node(elem)
                case 'MINOR-VERSION':
                    minor_version = self.parse_number_node(elem)
                case 'SERVICE-IDENTIFIER':
                    service_identifier = self.parse_int_node(elem)
                case 'INSTANCE-IDENTIFIER':
                    instance_identifier = self.parse_int_node(elem)
                case 'CONSUMED-EVENT-GROUPS':
                    consumed_event_groups = self._parse_element_list(
                        elem,
                        {'CONSUMED-EVENT-GROUP': self._parse_consumed_event_group},
                    )
                case 'LOCAL-UNICAST-ADDRESSS':
                    local_unicast_addresses = self._parse_element_list(
                        elem,
                        {'APPLICATION-ENDPOINT-REF-CONDITIONAL': self._parse_endpoint_ref},
                    )
                case 'METHOD-ACTIVATION-ROUTING-GROUPS' | 'SD-CLIENT-TIMER-CONFIGS':
                    self._logger.warning(f'Not implemented: {elem.tag}')
                case _:
                    self._logger.warning(f'Unexpected tag: {elem.tag}')
        instance = ConsumedServiceInstance(
            name=name,
            major_version=major_version,
            minor_version=minor_version,
            service_identifier=service_identifier,
            instance_identifier=instance_identifier,
            local_unicast_addresses=local_unicast_addresses,
            consumed_event_groups=consumed_event_groups,
        )
        return instance

    def _parse_provided_service_instance(self, xml_element: Element) -> ProvidedServiceInstance:
        name = None
        major_version = None
        minor_version = None
        instance_identifier = None
        service_identifier = None
        event_handlers = None
        local_unicast_addresses = None
        for elem in xml_element.findall('./*'):
            match elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(elem)
                case 'MAJOR-VERSION':
                    major_version = self.parse_int_node(elem)
                case 'MINOR-VERSION':
                    minor_version = self.parse_int_node(elem)
                case 'SERVICE-IDENTIFIER':
                    service_identifier = self.parse_int_node(elem)
                case 'INSTANCE-IDENTIFIER':
                    instance_identifier = self.parse_int_node(elem)
                case 'EVENT-HANDLERS':
                    event_handlers = self._parse_element_list(
                        elem,
                        {'EVENT-HANDLER': self._parse_event_handler},
                    )
                case 'LOCAL-UNICAST-ADDRESSS':
                    local_unicast_addresses = self._parse_element_list(
                        elem,
                        {'APPLICATION-ENDPOINT-REF-CONDITIONAL': self._parse_endpoint_ref},
                    )
                case 'METHOD-ACTIVATION-ROUTING-GROUPS' | 'SD-SERVER-TIMER-CONFIGS':
                    self._logger.warning(f'Not implemented: {elem.tag}')
                case _:
                    self._logger.warning(f'Unexpected tag: {elem.tag}')
        instance = ProvidedServiceInstance(
            name=name,
            major_version=major_version,
            minor_version=minor_version,
            service_identifier=service_identifier,
            instance_identifier=instance_identifier,
            local_unicast_addresses=local_unicast_addresses,
            event_handlers=event_handlers,
        )
        return instance

    def _parse_consumed_event_group(self, xml_element: Element) -> ConsumedEventGroup:
        name = None
        event_group_identifier = None
        activation_groups = None
        for elem in xml_element.findall('./*'):
            match elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(elem)
                case 'EVENT-GROUP-IDENTIFIER':
                    event_group_identifier = self.parse_int_node(elem)
                case 'PDU-ACTIVATION-ROUTING-GROUPS':
                    activation_groups = self._parse_element_list(
                        elem,
                        {'PDU-ACTIVATION-ROUTING-GROUP': self._parse_activation_routing_group},
                    )
                case 'LOCAL-UNICAST-ADDRESSS' | 'SD-CLIENT-TIMER-CONFIGS':
                    self._logger.warning(f'Not implemented: {elem.tag}')
                case _:
                    self._logger.warning(f'Unexpected tag: {elem.tag}')
        event_group = ConsumedEventGroup(
            name=name,
            event_group_identifier=event_group_identifier,
            pdu_activation_routing_groups=activation_groups,
        )
        return event_group

    def _parse_event_handler(self, xml_element: Element) -> EventHandler:
        name = None
        event_group_identifier = None
        multicast_threshold = None
        activation_groups = None
        for elem in xml_element.findall('./*'):
            match elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(elem)
                case 'EVENT-GROUP-IDENTIFIER':
                    event_group_identifier = self.parse_int_node(elem)
                case 'MULTICAST-THRESHOLD':
                    multicast_threshold = self.parse_int_node(elem)
                case 'PDU-ACTIVATION-ROUTING-GROUPS':
                    activation_groups = self._parse_element_list(
                        elem,
                        {'PDU-ACTIVATION-ROUTING-GROUP': self._parse_activation_routing_group},
                    )
                case 'LOCAL-UNICAST-ADDRESSS' | 'SD-SERVER-EG-TIMER-CONFIGS':
                    self._logger.warning(f'Not implemented: {elem.tag}')
                case _:
                    self._logger.warning(f'Unexpected tag: {elem.tag}')
        event_handler = EventHandler(
            name=name,
            event_group_identifier=event_group_identifier,
            multicast_threshold=multicast_threshold,
            pdu_activation_routing_groups=activation_groups,
        )
        return event_handler

    def _parse_endpoint_ref(self, xml_elem: Element) -> ApplicationEndpointRefConditional:
        name = None
        app_endpoint_ref = None
        for elem in xml_elem.findall('./*'):
            match elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(elem)
                case 'APPLICATION-ENDPOINT-REF':
                    app_endpoint_ref = self.parse_text_node(elem)
                case _:
                    self._logger.warning(f'Unexpected tag: {elem.tag}')
        endpoint_ref = ApplicationEndpointRefConditional(
            name=name,
            application_endpoint_ref=app_endpoint_ref,
        )
        return endpoint_ref

    def _parse_activation_routing_group(self, xml_elem: Element) -> PDUActivationRoutingGroup:
        name = None
        control_type = None
        udp_refs = []
        tcp_refs = []
        for elem in xml_elem.findall('./*'):
            match elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(elem)
                case 'EVENT-GROUP-CONTROL-TYPE':
                    control_type = self.parse_text_node(elem)
                case 'I-PDU-IDENTIFIER-UDP-REFS':
                    for child_elem in elem.findall('./*'):
                        if child_elem.tag != 'I-PDU-IDENTIFIER-UDP-REF':
                            self._logger.error(f'Unexpected tag for {elem.tag}: {child_elem.tag}')
                            continue
                        udp_refs.append(self.parse_text_node(child_elem))
                case 'I-PDU-IDENTIFIER-TCP-REFS':
                    for child_elem in elem.findall('./*'):
                        if child_elem.tag != 'I-PDU-IDENTIFIER-TCP-REF':
                            self._logger.error(f'Unexpected tag for {elem.tag}: {child_elem.tag}')
                            continue
                        tcp_refs.append(self.parse_text_node(child_elem))
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {elem.tag}')
        activation_group = PDUActivationRoutingGroup(
            name=name,
            event_group_control_type=control_type,
            i_pdu_identifier_udp_refs=udp_refs,
            i_pdu_identifier_tcp_refs=tcp_refs,
        )
        return activation_group
