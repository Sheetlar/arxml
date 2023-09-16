from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.data_transformation import (
    DataTransformationSet,
    DataTransformation,
    TransformationTechnology,
    EndToEndTransformationDescription,
    SomeIpTransformationDescription,
)
from autosar.parser.datatype_parser import BufferPropertiesParser
from autosar.parser.parser_base import ElementParser


class DataTransformationSetParser(ElementParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buffer_props_parser = BufferPropertiesParser(*args, **kwargs)

    def get_supported_tags(self):
        return ['DATA-TRANSFORMATION-SET']

    def parse_element(self, xml_element: Element, parent: ArObject | None = None):
        if xml_element.tag == 'DATA-TRANSFORMATION-SET':
            return self._parse_transformation_set(xml_element, parent)
        return None

    def _parse_transformation_set(self, xml_elem: Element, parent: ArObject | None) -> DataTransformationSet:
        name = None
        transformations = None
        technologies = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(child_elem)
                case 'DATA-TRANSFORMATIONS':
                    transformations = self._parse_element_list(
                        child_elem,
                        {'DATA-TRANSFORMATION': self._parse_transformation},
                    )
                case 'TRANSFORMATION-TECHNOLOGYS':
                    technologies = self._parse_element_list(
                        child_elem,
                        {'TRANSFORMATION-TECHNOLOGY': self._parse_transformation_technology},
                    )
                case _:
                    self._logger.warning(f'Unexpected tag: {child_elem.tag}')
        transformation_set = DataTransformationSet(
            name=name,
            data_transformations=transformations,
            transformation_technologies=technologies,
            parent=parent,
        )
        return transformation_set

    def _parse_transformation(self, xml_elem: Element) -> DataTransformation:
        name = None
        execute = False
        transformer_refs = []
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(child_elem)
                case 'EXECUTE-DESPITE-DATA-UNAVAILABILITY':
                    execute = self.parse_boolean_node(child_elem)
                case 'TRANSFORMER-CHAIN-REFS':
                    for sub_elem in child_elem.findall('./*'):
                        if sub_elem.tag != 'TRANSFORMER-CHAIN-REF':
                            self._logger.error(f'Unexpected tag: {sub_elem.tag}')
                        ref = self.parse_text_node(sub_elem)
                        if ref is not None:
                            transformer_refs.append(ref)
                case _:
                    self._logger.warning(f'Unexpected tag: {child_elem.tag}')
        transformation = DataTransformation(
            name=name,
            execute_despite_data_unavailability=execute,
            transformer_chain_refs=transformer_refs,
        )
        return transformation

    def _parse_transformation_technology(self, xml_elem: Element) -> TransformationTechnology:
        name = None
        buffer_properties = None
        protocol = None
        transformer_class = None
        version = None
        has_internal_state = False
        needs_original_data = False
        descriptions = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(child_elem)
                case 'BUFFER-PROPERTIES':
                    buffer_properties = self._buffer_props_parser.parse_element(child_elem)
                case 'PROTOCOL':
                    protocol = self.parse_text_node(child_elem)
                case 'TRANSFORMER-CLASS':
                    transformer_class = self.parse_text_node(child_elem)
                case 'VERSION':
                    version = self.parse_number_node(child_elem)
                case 'HAS-INTERNAL-STATE':
                    has_internal_state = self.parse_boolean_node(child_elem)
                case 'NEEDS-ORIGINAL-DATA':
                    needs_original_data = self.parse_boolean_node(child_elem)
                case 'TRANSFORMATION-DESCRIPTIONS':
                    descriptions = self._parse_element_list(child_elem,{
                        'END-TO-END-TRANSFORMATION-DESCRIPTION': self._parse_e2e_description,
                        'SOMEIP-TRANSFORMATION-DESCRIPTION': self._parse_some_ip_description,
                    })
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        technology = TransformationTechnology(
            name=name,
            buffer_properties=buffer_properties,
            protocol=protocol,
            transformer_class=transformer_class,
            version=version,
            has_internal_state=has_internal_state,
            needs_original_data=needs_original_data,
            transformation_descriptions=descriptions,
        )
        return technology

    def _parse_e2e_description(self, xml_elem: Element) -> EndToEndTransformationDescription:
        counter_offset = self.parse_int_node(xml_elem.find('COUNTER-OFFSET'))
        crc_offset = self.parse_int_node(xml_elem.find('CRC-OFFSET'))
        offset = self.parse_int_node(xml_elem.find('OFFSET'))
        data_id_mode = self.parse_text_node(xml_elem.find('DATA-ID-MODE'))
        e2e_profile_compatibility_props_ref = self.parse_text_node(xml_elem.find('E-2-E-PROFILE-COMPATIBILITY-PROPS-REF'))
        max_delta_counter = self.parse_int_node(xml_elem.find('MAX-DELTA-COUNTER'))
        max_error_state_init = self.parse_int_node(xml_elem.find('MAX-ERROR-STATE-INIT'))
        max_error_state_invalid = self.parse_int_node(xml_elem.find('MAX-ERROR-STATE-INVALID'))
        max_error_state_valid = self.parse_int_node(xml_elem.find('MAX-ERROR-STATE-VALID'))
        max_no_new_or_repeated_data = self.parse_int_node(xml_elem.find('MAX-NO-NEW-OR-REPEATED-DATA'))
        min_ok_state_init = self.parse_int_node(xml_elem.find('MIN-OK-STATE-INIT'))
        min_ok_state_invalid = self.parse_int_node(xml_elem.find('MIN-OK-STATE-INVALID'))
        min_ok_state_valid = self.parse_int_node(xml_elem.find('MIN-OK-STATE-VALID'))
        profile_behavior = self.parse_text_node(xml_elem.find('PROFILE-BEHAVIOR'))
        profile_name = self.parse_text_node(xml_elem.find('PROFILE-NAME'))
        sync_counter_init = self.parse_int_node(xml_elem.find('SYNC-COUNTER-INIT'))
        upper_header_bits_to_shift = self.parse_int_node(xml_elem.find('UPPER-HEADER-BITS-TO-SHIFT'))
        window_size_init = self.parse_int_node(xml_elem.find('WINDOW-SIZE-INIT'))
        window_size_invalid = self.parse_int_node(xml_elem.find('WINDOW-SIZE-INVALID'))
        window_size_valid = self.parse_int_node(xml_elem.find('WINDOW-SIZE-VALID'))
        description = EndToEndTransformationDescription(
            counter_offset=counter_offset,
            crc_offset=crc_offset,
            offset=offset,
            data_id_model=data_id_mode,
            e2e_profile_compatibility_props_ref=e2e_profile_compatibility_props_ref,
            max_delta_counter=max_delta_counter,
            max_error_state_init=max_error_state_init,
            max_error_state_invalid=max_error_state_invalid,
            max_error_state_valid=max_error_state_valid,
            max_no_new_or_repeated_data=max_no_new_or_repeated_data,
            min_ok_state_init=min_ok_state_init,
            min_ok_state_invalid=min_ok_state_invalid,
            min_ok_state_valid=min_ok_state_valid,
            profile_behavior=profile_behavior,
            profile_name=profile_name,
            sync_counter_init=sync_counter_init,
            upper_header_bits_to_shift=upper_header_bits_to_shift,
            window_size_init=window_size_init,
            window_size_invalid=window_size_invalid,
            window_size_valid=window_size_valid,
        )
        return description

    def _parse_some_ip_description(self, xml_elem: Element) -> SomeIpTransformationDescription:
        alignment = self.parse_int_node(xml_elem.find('ALIGNMENT'))
        byte_order = self.parse_text_node(xml_elem.find('BYTE-ORDER'))
        version = self.parse_number_node(xml_elem.find('INTERFACE-VERSION'))
        description = SomeIpTransformationDescription(
            alignment=alignment,
            byte_order=byte_order,
            interface_version=version,
        )
        return description
