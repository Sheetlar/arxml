from typing import Callable
from xml.etree.ElementTree import Element

from autosar.model.ar_object import ArObject
from autosar.model.base import SwDataDefPropsVariants, ValueSpecification
from autosar.parser.parser_base import ElementParser
from autosar.model.signal import (
    SystemSignal,
    SystemSignalGroup,
    ISignal,
    ISignalGroup,
    ISignalProps,
    TransformationISignalPropsVariants,
    SomeIpTransformationISignalProps,
    SomeIpTransformationISignalPropsVariants,
    EndToEndTransformationISignalProps,
    EndToEndTransformationISignalPropsVariants,
    UserDefinedTransformationISignalProps,
    UserDefinedTransformationISignalPropsVariants,
)


class SignalParser(ElementParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.switcher: dict[str, Callable[[Element, ArObject | None], SystemSignal | ISignal | None]] = {
            'SYSTEM-SIGNAL': self.parse_system_signal,
            'SYSTEM-SIGNAL-GROUP': self.parse_system_signal_group,
            'I-SIGNAL': self.parse_i_signal,
            'I-SIGNAL-GROUP': self.parse_i_signal_group,
        }

    def get_supported_tags(self):
        return self.switcher.keys()

    def parse_element(
            self,
            xml_element: Element,
            parent: ArObject | None = None,
    ) -> SystemSignal | SystemSignalGroup | ISignal | None:
        parse_func = self.switcher.get(xml_element.tag)
        if parse_func is not None:
            return parse_func(xml_element, parent)
        return None

    def parse_system_signal_group(self, xml_elem: Element, parent: ArObject | None) -> SystemSignalGroup:
        common_args = self.parse_common_tags(xml_elem)
        system_signal_refs: list[str] | None = None
        transforming_signal_ref: str | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'SYSTEM-SIGNAL-REFS':
                    system_signal_refs = list(self.child_string_nodes(child_elem))
                case 'TRANSFORMING-SYSTEM-SIGNAL-REF':
                    transforming_signal_ref = self.parse_text_node(child_elem)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        return SystemSignalGroup(
            system_signal_refs=system_signal_refs,
            transforming_system_signal_ref=transforming_signal_ref,
            parent=parent,
            **common_args,
        )

    def parse_system_signal(self, xml_elem: Element, parent: ArObject | None) -> SystemSignal | None:
        common_args = self.parse_common_tags(xml_elem)
        dynamic_length: bool | None = None
        physical_props: SwDataDefPropsVariants | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'DYNAMIC-LENGTH':
                    dynamic_length = self.parse_boolean_node(child_elem)
                case 'PHYSICAL-PROPS':
                    physical_props = self.parse_sw_data_def_props(child_elem)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        return SystemSignal(
            dynamic_length=dynamic_length,
            physical_props=physical_props,
            parent=parent,
            **common_args,
        )

    def parse_i_signal(self, xml_elem: Element, parent: ArObject | None) -> ISignal:
        common_args = self.parse_common_tags(xml_elem)
        system_signal_ref: str | None = None
        data_type_policy: str | None = None
        length: int | None = None
        i_signal_type: str | None = None
        i_signal_props: ISignalProps | None = None
        transformation_refs: list[str] | None = None
        init_value: ValueSpecification | None = None
        network_props: SwDataDefPropsVariants | None = None
        timeout_substitution_value: ValueSpecification | None = None
        transformation_props: list[TransformationISignalPropsVariants] | None = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'SYSTEM-SIGNAL-REF':
                    system_signal_ref = self.parse_text_node(child_elem)
                case 'DATA-TYPE-POLICY':
                    data_type_policy = self.parse_text_node(child_elem)
                case 'LENGTH':
                    length = self.parse_int_node(child_elem)
                case 'I-SIGNAL-TYPE':
                    i_signal_type = self.parse_text_node(child_elem)
                case 'I-SIGNAL-PROPS':
                    i_signal_props = ISignalProps(self.parse_text_node(
                        child_elem.find('HANDLE-OUT-OF-RANGE'),
                    ))
                case 'DATA-TRANSFORMATIONS':
                    transformation_refs = list(self.variation_child_string_nodes(child_elem, 'DATA-TRANSFORMATION-REF'))
                case 'INIT-VALUE':
                    init_value = self.parse_value_specification(child_elem)
                case 'NETWORK-REPRESENTATION-PROPS':
                    network_props = self.parse_sw_data_def_props(child_elem)
                case 'TIMEOUT-SUBSTITUTION-VALUE':
                    timeout_substitution_value = self.parse_value_specification(child_elem)
                case 'TRANSFORMATION-I-SIGNAL-PROPSS':
                    transformation_props = self.parse_variable_element_list(child_elem, {
                        'END-TO-END-TRANSFORMATION-I-SIGNAL-PROPS': self._parse_end_to_end_transformation_props,
                        'SOMEIP-TRANSFORMATION-I-SIGNAL-PROPS': self._parse_some_ip_transformation_props,
                        'USER-DEFINED-TRANSFORMATION-I-SIGNAL-PROPS': self._parse_user_defined_transformation_props,
                    })
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        signal = ISignal(
            system_signal_ref=system_signal_ref,
            data_type_policy=data_type_policy,
            length=length,
            i_signal_type=i_signal_type,
            i_signal_props=i_signal_props,
            data_transformation_refs=transformation_refs,
            init_value=init_value,
            network_representation_props=network_props,
            timeout_substitution_value=timeout_substitution_value,
            transformation_i_signal_props=transformation_props,
            parent=parent,
            **common_args,
        )
        return signal

    def parse_i_signal_group(self, xml_elem: Element, parent: ArObject | None) -> ISignalGroup:
        common_args = self.parse_common_tags(xml_elem)
        signal_refs: list[str] | None = None
        system_signal_group_ref: str | None = None
        group_transformations: list[str] | None = None
        transformation_props: list[TransformationISignalPropsVariants] | None = None
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case tag if tag in self.common_tags:
                    pass
                case 'I-SIGNAL-REFS':
                    signal_refs = list(self.child_string_nodes(xml_elem))
                case 'SYSTEM-SIGNAL-GROUP-REF':
                    system_signal_group_ref = self.parse_text_node(child_elem)
                case 'COM-BASED-SIGNAL-GROUP-TRANSFORMATIONS':
                    group_transformations = list(self.variation_child_string_nodes(xml_elem, 'DATA-TRANSFORMATION-REF'))
                case 'TRANSFORMATION-I-SIGNAL-PROPSS':
                    transformation_props = self.parse_variable_element_list(child_elem, {
                        'END-TO-END-TRANSFORMATION-I-SIGNAL-PROPS': self._parse_end_to_end_transformation_props,
                        'SOMEIP-TRANSFORMATION-I-SIGNAL-PROPS': self._parse_some_ip_transformation_props,
                        'USER-DEFINED-TRANSFORMATION-I-SIGNAL-PROPS': self._parse_user_defined_transformation_props,
                    })
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        signal_group = ISignalGroup(
            i_signal_refs=signal_refs,
            system_signal_group_ref=system_signal_group_ref,
            com_based_signal_group_transformation_refs=group_transformations,
            transformation_i_signal_props=transformation_props,
            parent=parent,
            **common_args,
        )
        return signal_group

    def _parse_some_ip_transformation_props(self, xml_elem: Element) -> SomeIpTransformationISignalPropsVariants | None:
        def variants():
            for variant_elem in variants_elem.findall('SOMEIP-TRANSFORMATION-I-SIGNAL-PROPS-CONDITIONAL'):
                transformer_ref = self.parse_text_node(variant_elem.find('TRANSFORMER-REF'))
                if transformer_ref is None:
                    self.log_missing_required(variant_elem, 'TRANSFORMER-REF')
                    continue
                common_args = self.parse_common_tags(variant_elem)
                yield SomeIpTransformationISignalProps(
                    transformer_ref=transformer_ref,
                    cs_error_reaction=self.parse_text_node(variant_elem.find('CS-ERROR-REACTION')),
                    message_type=self.parse_text_node(variant_elem.find('MESSAGE-TYPE')),
                    interface_version=self.parse_int_node(variant_elem.find('INTERFACE-VERSION')),
                    is_dynamic_length_field_size=self.parse_boolean_node(variant_elem.find('IS-DYNAMIC-LENGTH-FIELD-SIZE')),
                    session_handling_sr=self.parse_text_node(variant_elem.find('SESSION-HANDLING-SR')),
                    size_of_array_length_fields=self.parse_int_node(variant_elem.find('SIZE-OF-ARRAY-LENGTH-FIELDS')),
                    size_of_string_length_fields=self.parse_int_node(variant_elem.find('SIZE-OF-STRING-LENGTH-FIELDS')),
                    size_of_struct_length_fields=self.parse_int_node(variant_elem.find('SIZE-OF-STRUCT-LENGTH-FIELDS')),
                    size_of_union_length_fields=self.parse_int_node(variant_elem.find('SIZE-OF-UNION-LENGTH-FIELDS')),
                    tlv_data_id_definition_refs=list(self.child_string_nodes(
                        variant_elem.find('TLV-DAT-ID-DEFINITION-REFS'),
                    )),
                    implements_legacy_string_serialization=self.parse_boolean_node(
                        variant_elem.find('IMPLEMENTS-SOMEIP-STRING-HANDLING'),
                    ),
                    **common_args,
                )

        variants_elem = xml_elem.find('SOMEIP-TRANSFORMATION-I-SIGNAL-PROPS-VARIANTS')
        if variants_elem is None:
            return None
        props = SomeIpTransformationISignalPropsVariants(variants=variants())
        return props

    def _parse_end_to_end_transformation_props(self, xml_elem: Element) -> EndToEndTransformationISignalPropsVariants | None:
        def variants():
            for variant_elem in variants_elem.findall('END-TO-END-TRANSFORMATION-I-SIGNAL-PROPS-CONDITIONAL'):
                transformer_ref = self.parse_text_node(variant_elem.find('TRANSFORMER-REF'))
                if transformer_ref is None:
                    self.log_missing_required(variant_elem, 'TRANSFORMER-REF')
                    continue
                common_args = self.parse_common_tags(variant_elem)
                yield EndToEndTransformationISignalProps(
                    transformer_ref=transformer_ref,
                    cs_error_reaction=self.parse_text_node(variant_elem.find('CS-ERROR-REACTION')),
                    data_ids=self.parse_element_list(variant_elem.find('DATA-IDS'), self.parse_int_node),
                    data_length=self.parse_int_node(variant_elem.find('DATA-LENGTH')),
                    max_data_length=self.parse_int_node(variant_elem.find('MAX-DATA-LENGTH')),
                    min_data_length=self.parse_int_node(variant_elem.find('MIN-DATA-LENGTH')),
                    source_id=self.parse_int_node(variant_elem.find('SOURCE-ID')),
                    **common_args,
                )

        variants_elem = xml_elem.find('END-TO-END-TRANSFORMATION-I-SIGNAL-PROPS-VARIANTS')
        if variants_elem is None:
            return None
        props = EndToEndTransformationISignalPropsVariants(variants=variants())
        return props

    def _parse_user_defined_transformation_props(self, xml_elem: Element) -> UserDefinedTransformationISignalPropsVariants | None:
        def variants():
            for variant_elem in variants_elem.findall('USER-DEFINED-TRANSFORMATION-I-SIGNAL-PROPS-CONDITIONAL'):
                transformer_ref = self.parse_text_node(variant_elem.find('TRANSFORMER-REF'))
                if transformer_ref is None:
                    self.log_missing_required(variant_elem, 'TRANSFORMER-REF')
                    continue
                common_args = self.parse_common_tags(variant_elem)
                yield UserDefinedTransformationISignalProps(
                    transformer_ref=transformer_ref,
                    cs_error_reaction=self.parse_text_node(variant_elem.find('CS-ERROR-REACTION')),
                    **common_args,
                )

        variants_elem = xml_elem.find('USER-DEFINED-TRANSFORMATION-I-SIGNAL-PROPS-VARIANTS')
        if variants_elem is None:
            return None
        props = UserDefinedTransformationISignalPropsVariants(variants=variants())
        return props
