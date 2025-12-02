from xml.etree.ElementTree import Element

from autosar.model.ar_object import ArObject
from autosar.parser.parser_base import ElementParser
from autosar.model.system import (
    System,
    SystemMapping,
    ClientServerToSignalMapping,
    SenderReceiverToSignalMapping,
    TriggerToSignalMapping,
    OperationInSystemInstanceRef,
    VariableDataPrototypeInSystemInstanceRef,
    TriggerInSystemInstanceRef,
    AnyDataMapping,
    AnyCryptoServiceMapping,
    SwcToEcuMapping,
    SecOcCryptoServiceMapping,
)


class SystemParser(ElementParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_supported_tags(self):
        return ['SYSTEM']

    def _parse_instance_ref_common_params(self, xml_elem: Element) -> dict[str, str]:
        port_ref: str | None = None
        composition_ref: str | None = None
        component_refs: list[str] | None = None
        base_ref: str | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case 'CONTEXT-PORT-REF':
                    port_ref = self.parse_text_node(child_elem)
                case 'CONTEXT-COMPOSITION-REF':
                    composition_ref = self.parse_text_node(child_elem)
                case 'CONTEXT-COMPONENT-REF':
                    ref = self.parse_text_node(child_elem)
                    if ref is not None:
                        component_refs = [ref]
                case 'CONTEXT-COMPONENT-REFS':
                    component_refs = list(self.child_string_nodes(child_elem))
                case 'BASE-REF':
                    base_ref = self.parse_text_node(child_elem)
        common_params = {
            'context_port_ref': port_ref,
            'context_composition_ref': composition_ref,
            'context_component_refs': component_refs,
            'base_ref': base_ref,
        }
        return self.not_none_dict(common_params)

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> System | None:
        if xml_element.tag == 'SYSTEM':
            return self.parse_system(xml_element, parent)
        return None

    def parse_system(self, xml_elem: Element, parent: ArObject | None = None) -> System | None:
        common_args = self.parse_common_tags(xml_elem)
        fibex_elements: list[str] | None = None
        mappings: list[SystemMapping] | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'FIBEX-ELEMENTS':
                    fibex_elements = list(self.variation_child_string_nodes(child_elem, 'FIBEX-ELEMENT-REF'))
                case 'MAPPINGS':
                    mappings = self.parse_element_list(
                        child_elem,
                        self._parse_system_mapping,
                        'SYSTEM-MAPPING',
                    )
                case 'SOFTWARE-COMPOSITION':
                    self.log_not_implemented(xml_elem, child_elem)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        if 'name' not in common_args:
            self.log_missing_required(xml_elem, 'SHORT-NAME')
            return None
        return System(
            fibex_element_refs=fibex_elements,
            mappings=mappings,
            parent=parent,
            **common_args,
        )

    def _parse_system_mapping(self, xml_elem: Element) -> SystemMapping:
        common_args = self.parse_common_tags(xml_elem)
        crypto_map: list[AnyCryptoServiceMapping] | None = None
        data_map: list[AnyDataMapping] | None = None
        sw_map: list[SwcToEcuMapping] | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'CRYPTO-SERVICE-MAPPINGS':
                    crypto_map = self.parse_variable_element_list(child_elem, {
                        'SEC-OC-CRYPTO-SERVICE-MAPPING': self._parse_sec_oc_crypto_service_mapping,
                        # TODO: TLS parser
                    })
                case 'DATA-MAPPINGS':
                    data_map = self.parse_variable_element_list(child_elem, {
                        'CLIENT-SERVER-TO-SIGNAL-MAPPING': self._parse_client_server_mapping,
                        'SENDER-RECEIVER-TO-SIGNAL-MAPPING': self._parse_sender_receiver_mapping,
                        'TRIGGER-TO-SIGNAL-MAPPING': self._parse_trigger_mapping,
                    })
                case 'SW-MAPPINGS' | 'SW-IMPL-MAPPINGS':
                    self.log_not_implemented(xml_elem, child_elem)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        mapping = SystemMapping(
            crypto_service_mappings=crypto_map,
            data_mappings=data_map,
            sw_mappings=sw_map,
            **common_args,
        )
        return mapping

    def _parse_sec_oc_crypto_service_mapping(self, xml_elem: Element) -> SecOcCryptoServiceMapping:
        common_args = self.parse_common_tags(xml_elem)
        auth_ref = self.parse_text_node(xml_elem.find('AUTHENTICATION-REF'))
        svc_key_ref = self.parse_text_node(xml_elem.find('CRYPTO-SERVICE-KEY-REF'))
        svc_queue_ref = self.parse_text_node(xml_elem.find('CRYPTO-SERVICE-QUEUE-REF'))
        return SecOcCryptoServiceMapping(
            authentication_ref=auth_ref,
            crypto_service_key_ref=svc_key_ref,
            crypto_service_queue_ref=svc_queue_ref,
            **common_args,
        )

    def _parse_client_server_mapping(self, xml_elem: Element) -> ClientServerToSignalMapping:
        def parse_instance_ref() -> OperationInSystemInstanceRef | None:
            instance_ref_elem = xml_elem.find('CLIENT-SERVER-OPERATION-IREF')
            if instance_ref_elem is None:
                return None
            operation_ref = self.parse_text_node(instance_ref_elem.find('TARGET-OPERATION-REF'))
            common_params = self._parse_instance_ref_common_params(instance_ref_elem)
            return OperationInSystemInstanceRef(
                target_operation_ref=operation_ref,
                **common_params,
            )

        call_signal_ref = self.parse_text_node(xml_elem.find('CALL-SIGNAL-REF'))
        instance_ref = parse_instance_ref()
        return_signal_ref = self.parse_text_node(xml_elem.find('RETURN-SIGNAL-REF'))
        mapping = ClientServerToSignalMapping(
            call_signal_ref=call_signal_ref,
            client_server_operation_instance_ref=instance_ref,
            return_signal_ref=return_signal_ref,
        )
        return mapping

    def _parse_sender_receiver_mapping(self, xml_elem: Element) -> SenderReceiverToSignalMapping:
        def parse_instance_ref() -> VariableDataPrototypeInSystemInstanceRef | None:
            instance_ref_elem = xml_elem.find('DATA-ELEMENT-IREF')
            if instance_ref_elem is None:
                return None
            data_prototype_ref = self.parse_text_node(instance_ref_elem.find('TARGET-DATA-PROTOTYPE-REF'))
            common_params = self._parse_instance_ref_common_params(instance_ref_elem)
            return VariableDataPrototypeInSystemInstanceRef(
                target_data_prototype_ref=data_prototype_ref,
                **common_params,
            )

        system_signal_ref = self.parse_text_node(xml_elem.find('SYSTEM-SIGNAL-REF'))
        instance_ref = parse_instance_ref()
        # TODO: 2 more parameters
        mapping = SenderReceiverToSignalMapping(
            system_signal_ref=system_signal_ref,
            data_element_instance_ref=instance_ref,
        )
        return mapping

    def _parse_trigger_mapping(self, xml_elem: Element) -> TriggerToSignalMapping:
        def parse_instance_ref() -> TriggerInSystemInstanceRef | None:
            instance_ref_elem = xml_elem.find('TRIGGER-IREF')
            if instance_ref_elem is None:
                return None
            trigger_ref = self.parse_text_node(instance_ref_elem.find('TARGET-TRIGGER-REF'))
            common_params = self._parse_instance_ref_common_params(instance_ref_elem)
            return TriggerInSystemInstanceRef(
                target_trigger_ref=trigger_ref,
                **common_params,
            )

        system_signal_ref = self.parse_text_node(xml_elem.find('SYSTEM-SIGNAL-REF'))
        instance_ref = parse_instance_ref()
        mapping = TriggerToSignalMapping(
            system_signal_ref=system_signal_ref,
            trigger_instance_ref=instance_ref,
        )
        return mapping
