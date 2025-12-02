from typing import Callable, Iterable
from xml.etree.ElementTree import Element

from autosar.model.ar_object import ArObject
from autosar.model.pdu import (
    Pdu,
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
    UserDefinedPdu,
    UserDefinedIPdu,
    DcmIPdu,
    J1939DcmIPdu,
    TransmissionModeDeclaration,
    ModeDrivenTransmissionModeCondition,
    TransmissionModeCondition, TransmissionModeTiming, TimeRangeType, AbsoluteTolerance, RelativeTolerance, EventControlledTiming, CyclicTiming,
    ISignalIPduGroup,
)
from autosar.parser.parser_base import ElementParser


class PduParser(ElementParser):
    pdu_common_tags = ('LENGTH', 'HAS-DYNAMIC-LENGTH', 'CONTAINED-I-PDU-PROPS', 'UNUSED-BIT-PATTERN')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.switcher: dict[str, Callable[[Element, ArObject], Pdu | None]] = {
            'GENERAL-PURPOSE-PDU': self._parse_general_purpose_pdu,
            'NM-PDU': self._parse_nm_pdu,
            'USER-DEFINED-PDU': self._parse_user_defined_pdu,
            'CONTAINER-I-PDU': self._parse_container_i_pdu,
            'DCM-I-PDU': self._parse_dcm_i_pdu,
            'GENERAL-PURPOSE-I-PDU': self._parse_general_purpose_i_pdu,
            'I-SIGNAL-I-PDU': self._parse_i_signal_i_pdu,
            'J-1939-DCM-I-PDU': self._parse_j1939_dcm_i_pdu,
            'MULTIPLEXED-I-PDU': self._parse_multiplexed_i_pdu,
            'N-PDU': self._parse_n_pdu,
            'SECURED-I-PDU': self._parse_secured_i_pdu,
            'USER-DEFINED-I-PDU': self._parse_user_defined_i_pdu,
            'I-SIGNAL-I-PDU-GROUP': self._parse_i_signal_i_pdu_group,
        }

    def get_supported_tags(self):
        return self.switcher.keys()

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> Pdu | None:
        if xml_element.tag not in self.switcher:
            return None
        parser = self.switcher[xml_element.tag]
        return parser(xml_element, parent)

    def _parse_pdu_common_params(self, xml_elem: Element) -> dict[str, ...]:
        element_params = self.parse_common_tags(xml_elem)
        length = self.parse_int_node(xml_elem.find('LENGTH'))
        has_dynamic_length = self.parse_boolean_node(xml_elem.find('HAS-DYNAMIC-LENGTH'))
        contained_i_pdu_props = self._parse_contained_i_pdu_props(xml_elem.find('CONTAINED-I-PDU-PROPS'))
        pattern = self.parse_int_node(xml_elem.find('UNUSED-BIT-PATTERN'))
        common_params = {
            'length': length,
            'has_dynamic_length': has_dynamic_length,
            'contained_i_pdu_props': contained_i_pdu_props,
            'unused_bit_pattern': pattern,
        }
        return self.not_none_dict(common_params) | element_params

    def _parse_general_purpose_pdu(self, xml_elem: Element, parent: ArObject | None) -> GeneralPurposePdu:
        common_params = self._parse_pdu_common_params(xml_elem)
        pdu = GeneralPurposePdu(
            parent=parent,
            **common_params,
        )
        return pdu

    def _parse_nm_pdu(self, xml_elem: Element, parent: ArObject | None) -> NMPdu:
        common_params = self._parse_pdu_common_params(xml_elem)
        mappings = self.parse_element_list(
            xml_elem.find('I-SIGNAL-TO-I-PDU-MAPPINGS'),
            self._parse_i_signal_to_i_pdu_mapping,
        )
        data_information = self.parse_boolean_node(xml_elem.find('NM-DATA-INFORMATION'))
        vote_information = self.parse_boolean_node(xml_elem.find('NM-VOTE-INFORMATION'))
        nm_pdu = NMPdu(
            i_signal_to_i_pdu_mappings=mappings,
            nm_data_information=data_information,
            nm_vote_information=vote_information,
            parent=parent,
            **common_params,
        )
        return nm_pdu

    def _parse_user_defined_pdu(self, xml_elem: Element, parent: ArObject | None) -> UserDefinedPdu:
        common_params = self._parse_pdu_common_params(xml_elem)
        cdd_type = self.parse_text_node(xml_elem.find('CDD-TYPE'))
        pdu = UserDefinedPdu(
            cdd_type=cdd_type,
            parent=parent,
            **common_params,
        )
        return pdu

    def _parse_container_i_pdu(self, xml_elem: Element, parent: ArObject | None) -> ContainerIPdu:
        common_params = self._parse_pdu_common_params(xml_elem)
        triggering_props: list[ContainedIPduProps] | None = None
        triggering_refs: list[str] | None = None
        container_timeout: float | None = None
        container_trigger: str | None = None
        header_type: str | None = None
        min_rx_size: int | None = None
        min_tx_size: int | None = None
        rx_accept_contained_i_pdu: str | None = None
        threshold_size: int | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags or tag in self.pdu_common_tags:
                    pass
                case 'CONTAINED-I-PDU-TRIGGERING-PROPS':
                    triggering_props = self._parse_contained_i_pdu_props(child_elem)
                case 'CONTAINED-PDU-TRIGGERING-REFS':
                    triggering_refs = list(self.child_string_nodes(child_elem))
                case 'CONTAINER-TIMEOUT':
                    container_timeout = self.parse_number_node(child_elem)
                case 'CONTAINER-TRIGGER':
                    container_trigger = self.parse_text_node(child_elem)
                case 'HEADER-TYPE':
                    header_type = self.parse_text_node(child_elem)
                case 'MINIMUM-RX-CONTAINER-QUEUE-SIZE':
                    min_rx_size = self.parse_int_node(child_elem)
                case 'MINIMUM-TX-CONTAINER-QUEUE-SIZE':
                    min_tx_size = self.parse_int_node(child_elem)
                case 'RX-ACCEPT-CONTAINED-I-PDU':
                    rx_accept_contained_i_pdu = self.parse_text_node(child_elem)
                case 'THRESHOLD-SIZE':
                    threshold_size = self.parse_int_node(child_elem)
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        i_signal_i_pdu = ContainerIPdu(
            contained_i_pdu_triggering_props=triggering_props,
            contained_pdu_triggering_refs=triggering_refs,
            container_timeout=container_timeout,
            container_trigger=container_trigger,
            header_type=header_type,
            minimum_rx_container_queue_size=min_rx_size,
            minimum_tx_container_queue_size=min_tx_size,
            rx_accept_contained_i_pdu=rx_accept_contained_i_pdu,
            threshold_size=threshold_size,
            parent=parent,
            **common_params,
        )
        return i_signal_i_pdu

    def _parse_dcm_i_pdu(self, xml_elem: Element, parent: ArObject | None) -> DcmIPdu:
        common_params = self._parse_pdu_common_params(xml_elem)
        diag_type = self.parse_text_node(xml_elem.find('DIAG-PDU-TYPE'))
        pdu = DcmIPdu(
            diag_pdu_type=diag_type,
            parent=parent,
            **common_params,
        )
        return pdu

    def _parse_general_purpose_i_pdu(self, xml_elem: Element, parent: ArObject | None) -> GeneralPurposeIPdu:
        common_params = self._parse_pdu_common_params(xml_elem)
        i_signal_i_pdu = GeneralPurposeIPdu(
            parent=parent,
            **common_params,
        )
        return i_signal_i_pdu

    def _parse_i_signal_i_pdu(self, xml_elem: Element, parent: ArObject | None) -> ISignalIPdu | None:
        common_params = self._parse_pdu_common_params(xml_elem)
        timing_specs: list[IPduTiming] | None = None
        mappings: Iterable[ISignalToIPduMapping] | None = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case tag if tag in self.common_tags or tag in self.pdu_common_tags:
                    pass
                case 'I-PDU-TIMING-SPECIFICATIONS':
                    timing_specs = self.parse_element_list(
                        child_elem,
                        self._parse_i_pdu_timing,
                        'I-PDU-TIMING',
                    )
                case 'I-SIGNAL-TO-PDU-MAPPINGS':
                    mappings = self.parse_element_list(
                        child_elem,
                        self._parse_i_signal_to_i_pdu_mapping,
                        'I-SIGNAL-TO-I-PDU-MAPPING',
                    )
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        if 'unused_bit_pattern' not in common_params:
            self.log_missing_required(xml_elem, 'UNUSED-BIT-PATTERN')
            return None
        i_signal_i_pdu = ISignalIPdu(
            i_pdu_timing_specifications=timing_specs,
            i_signal_to_pdu_mappings=mappings,
            parent=parent,
            **common_params,
        )
        return i_signal_i_pdu

    def _parse_j1939_dcm_i_pdu(self, xml_elem: Element, parent: ArObject | None) -> J1939DcmIPdu:
        common_params = self._parse_pdu_common_params(xml_elem)
        msg_type = self.parse_int_node(xml_elem.find('DIAGNOSTIC-MESSAGE-TYPE'))
        pdu = J1939DcmIPdu(
            diagnostic_message_type=msg_type,
            parent=parent,
            **common_params,
        )
        return pdu

    def _parse_multiplexed_i_pdu(self, xml_elem: Element, parent: ArObject | None) -> MultiplexedIPdu:
        common_params = self._parse_pdu_common_params(xml_elem)
        selector_field_byte_order: str | None = None
        selector_field_length: int | None = None
        selector_field_start_position: int | None = None
        dynamic_parts: list[DynamicPart] | None = None
        static_parts: list[StaticPart] | None = None
        trigger_mode: str | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags or tag in self.pdu_common_tags:
                    pass
                case 'SELECTOR-FIELD-BYTE-ORDER':
                    selector_field_byte_order = self.parse_text_node(child_elem)
                case 'SELECTOR-FIELD-LENGTH':
                    selector_field_length = self.parse_int_node(child_elem)
                case 'SELECTOR-FIELD-START-POSITION':
                    selector_field_start_position = self.parse_int_node(child_elem)
                case 'DYNAMIC-PARTS':
                    dynamic_parts = self.parse_variable_element_list(
                        child_elem,
                        {'DYNAMIC-PART': self._parse_dynamic_part},
                    )
                case 'STATIC-PARTS':
                    static_parts = self.parse_variable_element_list(
                        child_elem,
                        {'STATIC-PART': self._parse_static_part},
                    )
                case 'TRIGGER-MODE':
                    trigger_mode = self.parse_text_node(child_elem)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        i_signal_i_pdu = MultiplexedIPdu(
            selector_field_byte_order=selector_field_byte_order,
            selector_field_length=selector_field_length,
            selector_field_start_position=selector_field_start_position,
            dynamic_parts=dynamic_parts,
            static_parts=static_parts,
            trigger_mode=trigger_mode,
            parent=parent,
            **common_params,
        )
        return i_signal_i_pdu

    def _parse_n_pdu(self, xml_elem: Element, parent: ArObject | None) -> NPdu:
        common_params = self._parse_pdu_common_params(xml_elem)
        n_pdu = NPdu(
            parent=parent,
            **common_params,
        )
        return n_pdu

    def _parse_secured_i_pdu(self, xml_elem: Element, parent: ArObject | None) -> SecuredIPdu | None:
        common_params = self._parse_pdu_common_params(xml_elem)
        payload_ref: str | None = None
        secure_comm_props: SecureCommunicationProps | None = None
        auth_props_ref: str | None = None
        freshness_props_ref: str | None = None
        use_as_cryptographic_i_pdu: bool | None = None
        dyn_runtime_length: bool | None = None
        secured_header: str | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags or tag in self.pdu_common_tags:
                    pass
                case 'PAYLOAD-REF':
                    payload_ref = self.parse_text_node(child_elem)
                case 'SECURE-COMMUNICATION-PROPS':
                    data_id = self.parse_int_node(child_elem.find('DATA-ID'))
                    auth_retries = self.parse_int_node(child_elem.find('AUTHENTICATION-RETRIES'))
                    freshness_len = self.parse_int_node(child_elem.find('AUTH-DATA-FRESHNESS-LENGTH'))
                    freshness_pos = self.parse_int_node(child_elem.find('AUTH-DATA-FRESHNESS-START-POSITION'))
                    auth_build_attempts = self.parse_int_node(child_elem.find('AUTHENTICATION-BUILD-ATTEMPTS'))
                    freshness_value_id = self.parse_int_node(child_elem.find('FRESHNESS-VALUE-ID'))
                    msg_link_len = self.parse_int_node(child_elem.find('MESSAGE-LINK-LENGTH'))
                    msg_link_pos = self.parse_int_node(child_elem.find('MESSAGE-LINK-POSITION'))
                    secondary_freshness_value_id = self.parse_int_node(child_elem.find('SECONDARY-FRESHNESS-VALUE-ID'))
                    secured_area_len = self.parse_int_node(child_elem.find('SECURED-AREA-LENGTH'))
                    secured_area_off = self.parse_int_node(child_elem.find('SECURED-AREA-OFFSET'))
                    secure_comm_props = SecureCommunicationProps(
                        data_id=data_id,
                        authentication_retries=auth_retries,
                        auth_data_freshness_length=freshness_len,
                        auth_data_freshness_start_position=freshness_pos,
                        authentication_build_attempts=auth_build_attempts,
                        freshness_value_id=freshness_value_id,
                        message_link_length=msg_link_len,
                        message_link_position=msg_link_pos,
                        secondary_freshness_value_id=secondary_freshness_value_id,
                        secured_area_length=secured_area_len,
                        secured_area_offset=secured_area_off,
                    )
                case 'AUTHENTICATION-PROPS-REF':
                    auth_props_ref = self.parse_text_node(child_elem)
                case 'FRESHNESS-PROPS-REF':
                    freshness_props_ref = self.parse_text_node(child_elem)
                case 'USE-AS-CRYPTOGRAPHIC-I-PDU':
                    use_as_cryptographic_i_pdu = self.parse_boolean_node(child_elem)
                case 'DYNAMIC-RUNTIME-LENGTH-HANDLING':
                    dyn_runtime_length = self.parse_boolean_node(child_elem)
                case 'USE-SECURED-PDU-HEADER':
                    secured_header = self.parse_text_node(child_elem)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        if payload_ref is None:
            self.log_missing_required(xml_elem, 'PAYLOAD-REF')
            return None
        if secure_comm_props is None:
            self.log_missing_required(xml_elem, 'SECURE-COMMUNICATION-PROPS')
            return None
        secured_i_pdu = SecuredIPdu(
            payload_ref=payload_ref,
            secure_communication_props=secure_comm_props,
            authentication_props_ref=auth_props_ref,
            freshness_props_ref=freshness_props_ref,
            use_as_cryptographic_i_pdu=use_as_cryptographic_i_pdu,
            dynamic_runtime_length_handling=dyn_runtime_length,
            use_secured_pdu_header=secured_header,
            parent=parent,
            **common_params,
        )
        return secured_i_pdu

    def _parse_user_defined_i_pdu(self, xml_elem: Element, parent: ArObject | None) -> UserDefinedIPdu:
        common_params = self._parse_pdu_common_params(xml_elem)
        cdd_type = self.parse_text_node(xml_elem.find('CDD-TYPE'))
        pdu = UserDefinedIPdu(
            cdd_type=cdd_type,
            parent=parent,
            **common_params,
        )
        return pdu

    def _parse_i_signal_i_pdu_group(self, xml_elem: Element, parent: ArObject | None) -> ISignalIPduGroup | None:
        common_args = self.parse_common_tags(xml_elem)
        comm_direction = self.parse_text_node(xml_elem.find('COMMUNICATION-DIRECTION'))
        if comm_direction is None:
            self.log_missing_required(xml_elem, 'COMMUNICATION-DIRECTION')
            return None
        comm_mode = self.parse_text_node(xml_elem.find('COMMUNICATION-MODE'))
        sub_group_refs = list(self.child_string_nodes(xml_elem.find('CONTAINED-I-SIGNAL-I-PDU-GROUP-REFS')))
        i_pdus = list(self.variation_child_string_nodes(xml_elem.find('I-SIGNAL-I-PDUS'), 'I-SIGNAL-I-PDU-REF'))
        nm_pdus = list(self.variation_child_string_nodes(xml_elem.find('NM-PDUS'), 'NM-PDU-REF'))
        group = ISignalIPduGroup(
            communication_direction=comm_direction,
            communication_mode=comm_mode,
            contained_i_signal_i_pdu_group_refs=sub_group_refs,
            i_signal_i_pdu_refs=i_pdus,
            nm_pdu_refs=nm_pdus,
            **common_args,
        )
        return group

    def _parse_contained_i_pdu_props(self, xml_elem: Element | None) -> ContainedIPduProps | None:
        if xml_elem is None:
            return None
        semantics = self.parse_text_node(xml_elem.find('COLLECTION-SEMANTICS'))
        triggering_ref = self.parse_text_node(xml_elem.find('CONTAINED-PDU-TRIGGERING-REF'))
        long_header = self.parse_int_node(xml_elem.find('HEADER-ID-LONG-HEADER'))
        short_header = self.parse_int_node(xml_elem.find('HEADER-ID-SHORT-HEADER'))
        offset = self.parse_int_node(xml_elem.find('OFFSET'))
        priority = self.parse_int_node(xml_elem.find('PRIORITY'))
        timeout = self.parse_number_node(xml_elem.find('TIMEOUT'))
        trigger = self.parse_text_node(xml_elem.find('TRIGGER'))
        uib_position = self.parse_int_node(xml_elem.find('UPDATE-INDICATION-BIT-POSITION'))
        contained_props = ContainedIPduProps(
            collection_semantics=semantics,
            contained_pdu_triggering_ref=triggering_ref,
            header_id_long_header=long_header,
            header_id_short_header=short_header,
            offset=offset,
            priority=priority,
            timeout=timeout,
            trigger=trigger,
            update_indication_bit_position=uib_position,
        )
        return contained_props

    def _parse_i_signal_to_i_pdu_mapping(self, xml_elem: Element) -> ISignalToIPduMapping:
        common_args = self.parse_common_tags(xml_elem)
        i_signal_ref = self.parse_text_node(xml_elem.find('I-SIGNAL-REF'))
        i_signal_group_ref = self.parse_text_node(xml_elem.find('I-SIGNAL-GROUP-REF'))
        byte_order = self.parse_text_node(xml_elem.find('PACKING-BYTE-ORDER'))
        start_pos = self.parse_int_node(xml_elem.find('START-POSITION'))
        transfer_property = self.parse_text_node(xml_elem.find('TRANSFER-PROPERTY'))
        uib_position = self.parse_int_node(xml_elem.find('UPDATE-INDICATION-BIT-POSITION'))
        mapping = ISignalToIPduMapping(
            i_signal_ref=i_signal_ref,
            i_signal_group_ref=i_signal_group_ref,
            packing_byte_order=byte_order,
            start_position=start_pos,
            transfer_property=transfer_property,
            update_indication_bit_position=uib_position,
            **common_args,
        )
        return mapping

    def _parse_i_pdu_timing(self, xml_elem: Element) -> IPduTiming:
        common_params = self._parse_pdu_common_params(xml_elem)
        delay = self.parse_number_node(xml_elem.find('MINIMUM-DELAY'))
        transmission_elem = xml_elem.find('TRANSMISSION-MODE-DECLARATION')
        transmission = TransmissionModeDeclaration(
            mode_driven_false_conditions=self.parse_element_list(
                transmission_elem.find('MODE-DRIVEN-FALSE-CONDITIONS'),
                self._parse_mode_driven_transmission_mode_condition,
                'MODE-DRIVEN-TRANSMISSION-MODE-CONDITION',
            ),
            mode_driven_true_conditions=self.parse_element_list(
                transmission_elem.find('MODE-DRIVEN-TRUE-CONDITIONS'),
                self._parse_mode_driven_transmission_mode_condition,
                'MODE-DRIVEN-TRANSMISSION-MODE-CONDITION',
            ),
            transmission_mode_conditions=self.parse_element_list(
                transmission_elem.find('TRANSMISSION-MODE-CONDITIONS'),
                self._parse_transmission_mode_condition,
            ),
            transmission_mode_false_timing=self._parse_transmission_mode_timing(
                transmission_elem.find('TRANSMISSION-MODE-FALSE-TIMING'),
            ),
            transmission_mode_true_timing=self._parse_transmission_mode_timing(
                transmission_elem.find('TRANSMISSION-MODE-TRUE-TIMING'),
            ),
        )
        timing = IPduTiming(
            minimum_delay=delay,
            transmission_mode_declaration=transmission,
            **common_params,
        )
        return timing

    def _parse_mode_driven_transmission_mode_condition(self, xml_elem: Element) -> ModeDrivenTransmissionModeCondition | None:
        if xml_elem is None:
            return None
        refs = list(self.child_string_nodes(xml_elem.find('MODE-DECLARATION-REFS')))
        if len(refs) == 0:
            return None
        return ModeDrivenTransmissionModeCondition(mode_declaration_refs=refs)

    def _parse_transmission_mode_condition(self, xml_elem: Element) -> TransmissionModeCondition | None:
        if xml_elem is None:
            return None
        signal_ref = self.parse_text_node(xml_elem.find('I-SIGNAL-IN-I-PDU-REF'))
        data_filter = self.parse_data_filter(xml_elem.find('DATA-FILTER'))
        if signal_ref is None:
            self.log_missing_required(xml_elem, 'I-SIGNAL-IN-I-PDU-REF')
            return None
        if data_filter is None:
            self.log_missing_required(xml_elem, 'DATA-FILTER')
            return None
        return TransmissionModeCondition(
            i_signal_in_i_pdu_ref=signal_ref,
            data_filter=data_filter,
        )

    def _parse_transmission_mode_timing(self, xml_elem: Element) -> TransmissionModeTiming | None:
        def get_cyclic_timing() -> CyclicTiming | None:
            if (ct_elem := xml_elem.find('CYCLIC-TIMING')) is None:
                return None
            if (period := self._parse_time_range_type(ct_elem.find('TIME-PERIOD'))) is None:
                self.log_missing_required(ct_elem, 'TIME-PERIOD')
                return None
            offset = self._parse_time_range_type(ct_elem.find('TIME-OFFSET'))
            return CyclicTiming(
                time_period=period,
                time_offset=offset,
            )

        def get_event_controlled_timing() -> EventControlledTiming | None:
            if (ect_elem := xml_elem.find('EVENT-CONTROLLED-TIMING')) is None:
                return None
            if (num_of_reps := self.parse_int_node(ect_elem.find('NUMBER-OF-REPETITIONS'))) is None:
                self.log_missing_required(ect_elem, 'NUMBER-OF-REPETITIONS')
                return None
            period = self._parse_time_range_type(ect_elem.find('REPETITION-PERIOD'))
            return EventControlledTiming(
                number_of_repetitions=num_of_reps,
                repetition_period=period,
            )

        if xml_elem is None:
            return None
        return TransmissionModeTiming(
            cyclic_timing=get_cyclic_timing(),
            event_controlled_timing=get_event_controlled_timing(),
        )

    def _parse_time_range_type(self, xml_elem: Element | None) -> TimeRangeType | None:
        def get_tolerance() -> AbsoluteTolerance | RelativeTolerance | None:
            if tolerance is None:
                return None
            subclass_tag_prefix = tolerance.tag.removesuffix('-TOLERANCE')
            tolerance_value = self.parse_number_node(tolerance.find(subclass_tag_prefix))
            if subclass_tag_prefix == 'ABSOLUTE':
                return AbsoluteTolerance(absolute=tolerance_value)
            if subclass_tag_prefix == 'RELATIVE':
                return RelativeTolerance(relative=tolerance_value)
            self._logger.warning(f'Unexpected subclass of TimeRangeTypeTolerance: {subclass_tag_prefix.capitalize()}Tolerance, ignoring')
            return None

        if xml_elem is None:
            return None
        value = self.parse_number_node(xml_elem.find('VALUE'))
        if value is None:
            self.log_missing_required(xml_elem, 'VALUE')
            return None
        tolerance = xml_elem.find('TOLERANCE/*')
        return TimeRangeType(
            value=value,
            tolerance=get_tolerance(),
        )

    def _parse_dynamic_part(self, xml_elem: Element) -> DynamicPart | None:
        positions: list[SegmentPosition] | None = None
        alternatives: list[DynamicPartAlternative] | None = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SEGMENT-POSITIONS':
                    positions = self.parse_element_list(child_elem, self._parse_segment_position)
                case 'DYNAMIC-PART-ALTERNATIVES':
                    alternatives = self.parse_element_list(child_elem, self._parse_part_alternative)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        if positions is None:
            self.log_missing_required(xml_elem, 'SEGMENT-POSITIONS')
            return None
        if alternatives is None:
            self.log_missing_required(xml_elem, 'DYNAMIC-PART-ALTERNATIVES')
            return None
        part = DynamicPart(
            segment_positions=positions,
            dynamic_part_alternatives=alternatives,
        )
        return part

    def _parse_static_part(self, xml_elem: Element) -> StaticPart | None:
        positions: list[SegmentPosition] | None = None
        ref: str | None = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SEGMENT-POSITIONS':
                    positions = self.parse_element_list(child_elem, self._parse_segment_position)
                case 'I-PDU-REF':
                    ref = self.parse_text_node(child_elem.find('I-PDU-REF'))
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        if ref is None:
            self.log_missing_required(xml_elem, 'I-PDU-REF')
            return None
        part = StaticPart(
            segment_positions=positions,
            i_pdu_ref=ref,
        )
        return part

    def _parse_segment_position(self, xml_elem: Element) -> SegmentPosition:
        byte_order = self.parse_text_node(xml_elem.find('SEGMENT-BYTE-ORDER'))
        length = self.parse_int_node(xml_elem.find('SEGMENT-LENGTH'))
        position = self.parse_int_node(xml_elem.find('SEGMENT-POSITION'))
        segment_pos = SegmentPosition(
            segment_byte_order=byte_order,
            segment_length=length,
            segment_position=position,
        )
        return segment_pos

    def _parse_part_alternative(self, xml_elem: Element) -> DynamicPartAlternative:
        ref = self.parse_text_node(xml_elem.find('I-PDU-REF'))
        initial = self.parse_boolean_node(xml_elem.find('INITIAL-DYNAMIC-PART'))
        field_code = self.parse_int_node(xml_elem.find('SELECTOR-FIELD-CODE'))
        alternative = DynamicPartAlternative(
            i_pdu_ref=ref,
            initial_dynamic_part=initial,
            selector_field_code=field_code,
        )
        return alternative


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
                    identifiers = self.parse_variable_element_list(
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
