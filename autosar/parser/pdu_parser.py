from typing import Callable
from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.pdu import (
    ISignalIPdu,
    ISignalToIPduMapping,
    IPduTiming,
    ContainerIPdu,
    GeneralPurposePdu,
    MultiplexedIPdu,
    DynamicPart,
    StaticPart,
    SegmentPosition,
    DynamicPartAlternative,
    SocketConnectionIPduIdentifierSet,
    SoConIPduIdentifier,
    NPdu,
    NMPdu,
    SecuredIPdu,
    SecureCommunicationProps,
    GeneralPurposeIPdu,
    ContainedIPduProps,
)
from autosar.parser.parser_base import ElementParser


class PduParser(ElementParser):
    pdu_common_tags = ('LENGTH', 'UNUSED-BIT-PATTERN')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.switcher: dict[str, Callable[[Element, ArObject], ArObject | None]] = {
            'I-SIGNAL-I-PDU': self._parse_i_signal_i_pdu,
            'CONTAINER-I-PDU': self._parse_container_i_pdu,
            'GENERAL-PURPOSE-PDU': self._parse_general_purpose_pdu,
            'MULTIPLEXED-I-PDU': self._parse_multiplexed_i_pdu,
            'N-PDU': self._parse_n_pdu,
            'NM-PDU': self._parse_nm_pdu,
            'SECURED-I-PDU': self._parse_secured_i_pdu,
            'GENERAL-PURPOSE-I-PDU': self._parse_general_purpose_i_pdu,
        }

    def get_supported_tags(self):
        return self.switcher.keys()

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> ISignalIPdu | None:
        if xml_element.tag not in self.switcher:
            return None
        parser = self.switcher[xml_element.tag]
        return parser(xml_element, parent)

    def _parse_pdu_common_params(self, xml_elem: Element) -> dict[str, ...]:
        element_params = self._parse_common_tags(xml_elem)
        length = self.parse_int_node(xml_elem.find('LENGTH'))
        unused_bit_pattern = self.parse_number_node(xml_elem.find('UNUSED-BIT-PATTERN'))
        common_params = {
            'length': length,
            'unused_bit_pattern': unused_bit_pattern,
            **element_params,
        }
        return common_params

    def _parse_i_signal_i_pdu(self, xml_elem: Element, parent: ArObject | None) -> ISignalIPdu:
        contained_props = None
        timing_specs = None
        mappings = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case tag if tag in self.common_tags or tag in self.pdu_common_tags:
                    pass
                case 'CONTAINED-I-PDU-PROPS':
                    semantics = self.parse_text_node(child_elem.find('COLLECTION-SEMANTICS'))
                    offset = self.parse_int_node(child_elem.find('OFFSET'))
                    trigger = self.parse_text_node(child_elem.find('TRIGGER'))
                    contained_props = ContainedIPduProps(
                        collection_semantics=semantics,
                        offset=offset,
                        trigger=trigger,
                    )
                case 'I-PDU-TIMING-SPECIFICATIONS':
                    timing_specs = self._parse_element_list(
                        child_elem,
                        {'I-PDU-TIMING': self._parse_i_pdu_timing},
                    )
                case 'I-SIGNAL-TO-PDU-MAPPINGS':
                    mappings = self._parse_element_list(
                        child_elem,
                        {'I-SIGNAL-TO-I-PDU-MAPPING': self._parse_i_signal_to_i_pdu_mapping},
                    )
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        common_params = self._parse_pdu_common_params(xml_elem)
        i_signal_i_pdu = ISignalIPdu(
            contained_i_pdu_props=contained_props,
            i_pdu_timing_specifications=timing_specs,
            i_signal_to_pdu_mappings=mappings,
            parent=parent,
            **common_params,
        )
        return i_signal_i_pdu

    def _parse_i_pdu_timing(self, xml_elem: Element) -> IPduTiming:
        return IPduTiming()  # TODO: Implement later

    def _parse_i_signal_to_i_pdu_mapping(self, xml_elem: Element) -> ISignalToIPduMapping:
        common_args = self._parse_common_tags(xml_elem)
        i_signal_ref = self.parse_text_node(xml_elem.find('I-SIGNAL-REF'))
        byte_order = self.parse_text_node(xml_elem.find('PACKING-BYTE-ORDER'))
        start_pos = self.parse_int_node(xml_elem.find('START-POSITION'))
        transfer_property = self.parse_text_node(xml_elem.find('TRANSFER-PROPERTY'))
        mapping = ISignalToIPduMapping(
            i_signal_ref=i_signal_ref,
            packing_byte_order=byte_order,
            start_position=start_pos,
            transfer_property=transfer_property,
            **common_args,
        )
        return mapping

    def _parse_container_i_pdu(self, xml_elem: Element, parent: ArObject | None) -> ContainerIPdu:
        contained_pdu_triggering_refs = []
        container_trigger = None
        header_type = None
        rx_accept_contained_i_pdu = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case tag if tag in self.common_tags or tag in self.pdu_common_tags:
                    pass
                case 'CONTAINED-PDU-TRIGGERING-REFS':
                    for sub_elem in child_elem.findall('./*'):
                        if sub_elem.tag != 'CONTAINED-PDU-TRIGGERING-REF':
                            self._logger.error(f'Unexpected tag for {child_elem.tag}: {sub_elem.tag}')
                            continue
                        ref = self.parse_text_node(sub_elem)
                        if ref is not None:
                            contained_pdu_triggering_refs.append(ref)
                case 'CONTAINER-TRIGGER':
                    container_trigger = self.parse_text_node(child_elem)
                case 'HEADER-TYPE':
                    header_type = self.parse_text_node(child_elem)
                case 'RX-ACCEPT-CONTAINED-I-PDU':
                    rx_accept_contained_i_pdu = self.parse_text_node(child_elem)
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        common_params = self._parse_pdu_common_params(xml_elem)
        i_signal_i_pdu = ContainerIPdu(
            contained_pdu_triggering_refs=contained_pdu_triggering_refs,
            container_trigger=container_trigger,
            header_type=header_type,
            rx_accept_contained_i_pdu=rx_accept_contained_i_pdu,
            parent=parent,
            **common_params,
        )
        return i_signal_i_pdu

    def _parse_general_purpose_pdu(self, xml_elem: Element, parent: ArObject | None) -> GeneralPurposePdu:
        common_params = self._parse_pdu_common_params(xml_elem)
        i_signal_i_pdu = GeneralPurposePdu(
            parent=parent,
            **common_params,
        )
        return i_signal_i_pdu

    def _parse_multiplexed_i_pdu(self, xml_elem: Element, parent: ArObject | None) -> MultiplexedIPdu:
        dynamic_parts = None
        selector_field_byte_order = None
        selector_field_length = None
        selector_field_start_position = None
        static_parts = None
        trigger_mode = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case tag if tag in self.common_tags or tag in self.pdu_common_tags:
                    pass
                case 'DYNAMIC-PARTS':
                    dynamic_parts = self._parse_element_list(
                        child_elem,
                        {'DYNAMIC-PART': self._parse_dynamic_part},
                    )
                case 'STATIC-PARTS':
                    static_parts = self._parse_element_list(
                        child_elem,
                        {'STATIC-PART': self._parse_static_part},
                    )
                case 'SELECTOR-FIELD-BYTE-ORDER':
                    selector_field_byte_order = self.parse_text_node(child_elem)
                case 'SELECTOR-FIELD-LENGTH':
                    selector_field_length = self.parse_int_node(child_elem)
                case 'SELECTOR-FIELD-START-POSITION':
                    selector_field_start_position = self.parse_int_node(child_elem)
                case 'TRIGGER-MODE':
                    trigger_mode = self.parse_text_node(child_elem)
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        common_params = self._parse_pdu_common_params(xml_elem)
        i_signal_i_pdu = MultiplexedIPdu(
            dynamic_parts=dynamic_parts,
            selector_field_byte_order=selector_field_byte_order,
            selector_field_length=selector_field_length,
            selector_field_start_position=selector_field_start_position,
            static_parts=static_parts,
            trigger_mode=trigger_mode,
            parent=parent,
            **common_params,
        )
        return i_signal_i_pdu

    def _parse_dynamic_part(self, xml_elem: Element) -> DynamicPart:
        positions = []
        alternatives = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SEGMENT-POSITIONS':
                    byte_order = self.parse_text_node(child_elem.find('SEGMENT-BYTE-ORDER'))
                    length = self.parse_text_node(child_elem.find('SEGMENT-LENGTH'))
                    position = self.parse_text_node(child_elem.find('SEGMENT-POSITION'))
                    segment_pos = SegmentPosition(
                        segment_byte_order=byte_order,
                        segment_length=length,
                        segment_position=position,
                    )
                    positions.append(segment_pos)
                case 'DYNAMIC-PART-ALTERNATIVES':
                    alternatives = self._parse_element_list(
                        child_elem,
                        {'DYNAMIC-PART-ALTERNATIVE': self._parse_part_alternative},
                    )
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        dyn_part = DynamicPart(
            segment_positions=positions,
            dynamic_part_alternatives=alternatives,
        )
        return dyn_part

    def _parse_part_alternative(self, xml_elem: Element) -> DynamicPartAlternative:
        ref = self.parse_text_node(xml_elem.find('I-PDU-REF'))
        initial = self.parse_boolean_node(xml_elem.find('INITIAL-DYNAMIC-PART'))
        field_code = self.parse_number_node(xml_elem.find('SELECTOR-FIELD-CODE'))
        alternative = DynamicPartAlternative(
            i_pdu_ref=ref,
            initial_dynamic_part=initial,
            selector_field_code=field_code,
        )
        return alternative

    def _parse_static_part(self, xml_elem: Element) -> StaticPart:
        positions = []
        ref = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SEGMENT-POSITIONS':
                    byte_order = self.parse_text_node(child_elem.find('SEGMENT-BYTE-ORDER'))
                    length = self.parse_text_node(child_elem.find('SEGMENT-LENGTH'))
                    position = self.parse_text_node(child_elem.find('SEGMENT-POSITION'))
                    segment_pos = SegmentPosition(
                        segment_byte_order=byte_order,
                        segment_length=length,
                        segment_position=position,
                    )
                    positions.append(segment_pos)
                case 'I-PDU-REF':
                    ref = self.parse_text_node(child_elem.find('I-PDU-REF'))
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        part = StaticPart(
            segment_positions=positions,
            i_pdu_ref=ref,
        )
        return part

    def _parse_n_pdu(self, xml_elem: Element, parent: ArObject | None) -> NPdu:
        common_params = self._parse_pdu_common_params(xml_elem)
        n_pdu = NPdu(
            parent=parent,
            **common_params,
        )
        return n_pdu

    def _parse_nm_pdu(self, xml_elem: Element, parent: ArObject | None) -> NMPdu:
        common_params = self._parse_pdu_common_params(xml_elem)
        nm_pdu = NMPdu(
            parent=parent,
            **common_params,
        )
        return nm_pdu

    def _parse_secured_i_pdu(self, xml_elem: Element, parent: ArObject | None) -> SecuredIPdu:
        contained_props = None
        authentication_props_ref = None
        freshness_props_ref = None
        payload_ref = None
        secure_communication_props = None
        use_as_cryptographic_i_pdu = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case tag if tag in self.common_tags or tag in self.pdu_common_tags:
                    pass
                case 'CONTAINED-I-PDU-PROPS':
                    semantics = self.parse_text_node(child_elem.find('COLLECTION-SEMANTICS'))
                    offset = self.parse_int_node(child_elem.find('OFFSET'))
                    trigger = self.parse_text_node(child_elem.find('TRIGGER'))
                    contained_props = ContainedIPduProps(
                        collection_semantics=semantics,
                        offset=offset,
                        trigger=trigger,
                    )
                case 'AUTHENTICATION-PROPS-REF':
                    authentication_props_ref = self.parse_text_node(child_elem)
                case 'FRESHNESS-PROPS-REF':
                    freshness_props_ref = self.parse_text_node(child_elem)
                case 'PAYLOAD-REF':
                    payload_ref = self.parse_text_node(child_elem)
                case 'SECURE-COMMUNICATION-PROPS':
                    authentication_build_attempts = self.parse_number_node(child_elem.find('AUTHENTICATION-BUILD-ATTEMPTS'))
                    authentication_retries = self.parse_number_node(child_elem.find('AUTHENTICATION-RETRIES'))
                    data_id = self.parse_number_node(child_elem.find('DATA-ID'))
                    freshness_value_id = self.parse_number_node(child_elem.find('FRESHNESS-VALUE-ID'))
                    message_link_length = self.parse_number_node(child_elem.find('MESSAGE-LINK-LENGTH'))
                    message_link_position = self.parse_number_node(child_elem.find('MESSAGE-LINK-POSITION'))
                    secure_communication_props = SecureCommunicationProps(
                        authentication_build_attempts=authentication_build_attempts,
                        authentication_retries=authentication_retries,
                        data_id=data_id,
                        freshness_value_id=freshness_value_id,
                        message_link_length=message_link_length,
                        message_link_position=message_link_position,
                    )
                case 'USE-AS-CRYPTOGRAPHIC-I-PDU':
                    use_as_cryptographic_i_pdu = self.parse_boolean_node(child_elem)
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        common_params = self._parse_pdu_common_params(xml_elem)
        secured_i_pdu = SecuredIPdu(
            contained_i_pdu_props=contained_props,
            authentication_props_ref=authentication_props_ref,
            freshness_props_ref=freshness_props_ref,
            payload_ref=payload_ref,
            secure_communication_props=secure_communication_props,
            use_as_cryptographic_i_pdu=use_as_cryptographic_i_pdu,
            parent=parent,
            **common_params,
        )
        return secured_i_pdu

    def _parse_general_purpose_i_pdu(self, xml_elem: Element, parent: ArObject | None) -> GeneralPurposeIPdu:
        common_params = self._parse_pdu_common_params(xml_elem)
        i_signal_i_pdu = GeneralPurposeIPdu(
            parent=parent,
            **common_params,
        )
        return i_signal_i_pdu


class SoConSetParser(ElementParser):
    def get_supported_tags(self):
        return ['SOCKET-CONNECTION-IPDU-IDENTIFIER-SET']

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> SocketConnectionIPduIdentifierSet | None:
        if xml_element.tag == 'SOCKET-CONNECTION-IPDU-IDENTIFIER-SET':
            return self._parse_identifier_set(xml_element, parent)
        return None

    def _parse_identifier_set(self, xml_elem: Element, parent: ArObject | None) -> SocketConnectionIPduIdentifierSet:
        name = None
        identifiers = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(child_elem)
                case 'I-PDU-IDENTIFIERS':
                    identifiers = self._parse_element_list(
                        child_elem,
                        {'SO-CON-I-PDU-IDENTIFIER': self._parse_so_con_identifier},
                    )
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        identifier_set = SocketConnectionIPduIdentifierSet(
            name=name,
            i_pdu_identifiers=identifiers,
            parent=parent,
        )
        return identifier_set

    def _parse_so_con_identifier(self, xml_elem: Element) -> SoConIPduIdentifier:
        name = self.parse_text_node(xml_elem.find('SHORT-NAME'))
        header_id = self.parse_int_node(xml_elem.find('HEADER-ID'))
        triggering_ref = self.parse_text_node(xml_elem.find('PDU-TRIGGERING-REF'))
        identifier = SoConIPduIdentifier(
            name=name,
            header_id=header_id,
            pdu_triggering_ref=triggering_ref,
        )
        return identifier
