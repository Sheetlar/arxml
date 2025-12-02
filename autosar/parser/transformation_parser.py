from typing import Callable, TypeAlias
from xml.etree.ElementTree import Element

from autosar.model.ar_object import ArObject
from autosar.model.transformation import (
    DataTransformationSet,
    DataTransformation,
    TransformationTechnology,
    BufferProperties,
    EndToEndTransformationDescription,
    SomeIpTransformationDescription,
    UserDefinedTransformationDescription,
    TransformationPropsSet,
    SOMEIPTransformationProps,
    UserDefinedTransformationProps,
)
from autosar.parser.compu_parser import CompuParser
from autosar.parser.parser_base import ElementParser

TransformationObject: TypeAlias = DataTransformationSet | TransformationPropsSet


class TransformationParser(ElementParser, CompuParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.switcher: dict[str, Callable[[Element, ArObject | None], TransformationObject | None]] = {
            'DATA-TRANSFORMATION-SET': self._parse_data_transformation_set,
            'TRANSFORMATION-PROPS-SET': self._parse_transformation_props_set,
        }

    def get_supported_tags(self):
        return self.switcher.keys()

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> TransformationObject | None:
        if xml_element.tag not in self.switcher:
            return None
        element_parser = self.switcher[xml_element.tag]
        return element_parser(xml_element, parent)

    def _parse_data_transformation_set(self, xml_elem: Element, parent: ArObject | None) -> DataTransformationSet:
        common_args = self.parse_common_tags(xml_elem)
        transformations: list[DataTransformation] | None = None
        technologies: list[TransformationTechnology] | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'DATA-TRANSFORMATIONS':
                    transformations = self.parse_element_list(
                        child_elem,
                        self._parse_transformation,
                    )
                case 'TRANSFORMATION-TECHNOLOGYS' | 'TRANSFORMATION-TECHNOLOGIES':
                    technologies = self.parse_element_list(
                        child_elem,
                        self._parse_transformation_technology,
                        'TRANSFORMATION-TECHNOLOGY',
                    )
                case _:
                    self._logger.warning(f'Unexpected tag: {child_elem.tag}')
        transformation_set = DataTransformationSet(
            data_transformations=transformations,
            transformation_technologies=technologies,
            parent=parent,
            **common_args,
        )
        return transformation_set

    def _parse_transformation(self, xml_elem: Element) -> DataTransformation:
        common_args = self.parse_common_tags(xml_elem)
        transformer_refs: list[str] = []
        execute: bool | None = None
        kind: str | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'TRANSFORMER-CHAIN-REFS':
                    transformer_refs = list(self.child_string_nodes(child_elem))
                case 'EXECUTE-DESPITE-DATA-UNAVAILABILITY':
                    execute = self.parse_boolean_node(child_elem)
                case 'DATA-TRANSFORMATION-KIND':
                    kind = self.parse_text_node(child_elem)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        transformation = DataTransformation(
            transformer_chain_refs=transformer_refs,
            execute_despite_data_unavailability=execute,
            data_transformation_kind=kind,
            **common_args,
        )
        return transformation

    def _parse_transformation_technology(self, xml_elem: Element) -> TransformationTechnology:
        common_args = self.parse_common_tags(xml_elem)
        protocol: str | None = None
        version: str | None = None
        transformer_class: str | None = None
        buffer_properties = None
        has_internal_state: bool | None = None
        needs_original_data: bool | None = None
        descriptions: list | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'PROTOCOL':
                    protocol = self.parse_text_node(child_elem)
                case 'VERSION':
                    version = self.parse_text_node(child_elem)
                case 'TRANSFORMER-CLASS':
                    transformer_class = self.parse_text_node(child_elem)
                case 'BUFFER-PROPERTIES':
                    buffer_properties = self._parse_buffer_properties(child_elem)
                case 'HAS-INTERNAL-STATE':
                    has_internal_state = self.parse_boolean_node(child_elem)
                case 'NEEDS-ORIGINAL-DATA':
                    needs_original_data = self.parse_boolean_node(child_elem)
                case 'TRANSFORMATION-DESCRIPTIONS':
                    descriptions = self.parse_variable_element_list(child_elem, {
                        'END-TO-END-TRANSFORMATION-DESCRIPTION': self._parse_e2e_description,
                        'SOMEIP-TRANSFORMATION-DESCRIPTION': self._parse_some_ip_description,
                        'USER-DEFINED-TRANSFORMATION-DESCRIPTION': self._parse_user_defined_description,
                    })
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        technology = TransformationTechnology(
            protocol=protocol,
            version=version,
            transformer_class=transformer_class,
            buffer_properties=buffer_properties,
            has_internal_state=has_internal_state,
            needs_original_data=needs_original_data,
            transformation_descriptions=descriptions,
            **common_args,
        )
        return technology

    def _parse_buffer_properties(self, xml_elem: Element) -> BufferProperties | None:
        length = self.parse_int_node(xml_elem.find('HEADER-LENGTH'))
        if length is None:
            self.log_missing_required(xml_elem, 'HEADER-LENGTH')
            return None
        inplace = self.parse_boolean_node(xml_elem.find('IN-PLACE'))
        if inplace is None:
            self.log_missing_required(xml_elem, 'IN-PLACE')
            return None
        compu = self.parse_compu_scale(xml_elem.find('BUFFER-COMPUTATION'))
        return BufferProperties(
            header_length=length,
            in_place=inplace,
            buffer_computation=compu,
        )

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

    @staticmethod
    def _parse_user_defined_description(*_) -> UserDefinedTransformationDescription:
        return UserDefinedTransformationDescription()

    def _parse_transformation_props_set(self, xml_elem: Element, parent: ArObject | None) -> TransformationPropsSet:
        common_args = self.parse_common_tags(xml_elem)
        props = self.parse_variable_element_list(
            xml_elem.find('TRANSFORMATION-PROPSS'),
            {
                'SOMEIP-TRANSFORMATION-PROPS': self._parse_someip_transformation_props,
                'USER-DEFINED-TRANSFORMATION-PROPS': self._parse_user_defined_transformation_props,
            },
        )
        return TransformationPropsSet(
            transformation_props=props,
            parent=parent,
            **common_args,
        )

    def _parse_someip_transformation_props(self, xml_elem: Element) -> SOMEIPTransformationProps:
        common_args = self.parse_common_tags(xml_elem)
        return SOMEIPTransformationProps(
            alignment=self.parse_int_node(xml_elem.find('ALIGNMENT')),
            size_of_array_length_field=self.parse_int_node(xml_elem.find('SIZE-OF-ARRAY-LENGTH-FIELD')),
            size_of_string_length_field=self.parse_int_node(xml_elem.find('SIZE-OF-STRING-LENGTH-FIELD')),
            size_of_struct_length_field=self.parse_int_node(xml_elem.find('SIZE-OF-STRUCT-LENGTH-FIELD')),
            size_of_union_length_field=self.parse_int_node(xml_elem.find('SIZE-OF-UNION-LENGTH-FIELD')),
            **common_args,
        )

    def _parse_user_defined_transformation_props(self, xml_elem: Element) -> UserDefinedTransformationProps:
        kwargs = self.parse_common_tags(xml_elem)
        return UserDefinedTransformationProps(**kwargs)
