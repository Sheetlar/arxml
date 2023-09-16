from typing import Callable
from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.base import parse_text_node, parse_int_node
from autosar.parser.parser_base import ElementParser
from autosar.signal import (
    SystemSignal,
    SystemSignalGroup,
    ISignal,
    ISignalGroup,
    SomeIpTransformationISignalProps,
    EndToEndTransformationISignalProps,
)


class SignalParser(ElementParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 3.0 <= self.version < 4.0:
            self.switcher: dict[str, Callable[[Element, ArObject | None], SystemSignal | SystemSignalGroup | None]] = {
                'SYSTEM-SIGNAL': self.parse_system_signal,
                'SYSTEM-SIGNAL-GROUP': self.parse_system_signal_group,
            }
        elif self.version >= 4.0:
            self.switcher: dict[str, Callable[[Element, ArObject | None], SystemSignal | ISignal | None]] = {
                'SYSTEM-SIGNAL': self.parse_system_signal_ar4,
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

    def parse_system_signal(self, xml_root: Element, parent: ArObject | None) -> SystemSignal | None:
        """
        parses <SYSTEM-SIGNAL>
        """
        assert (xml_root.tag == 'SYSTEM-SIGNAL')
        name = None
        data_type_ref = None
        init_value_ref = None
        length = None
        desc = None
        for elem in xml_root.findall('./*'):
            if elem.tag == 'SHORT-NAME':
                name = parse_text_node(elem)
            elif elem.tag == 'DATA-TYPE-REF':
                data_type_ref = parse_text_node(elem)
            elif elem.tag == 'INIT-VALUE-REF':
                init_value_ref = parse_text_node(elem)
            elif elem.tag == 'LENGTH':
                length = parse_int_node(elem)
            elif elem.tag == 'DESC':
                desc_xml = xml_root.find('DESC')
                if desc_xml is not None:
                    l2_xml = desc_xml.find('L-2')
                    if l2_xml is not None:
                        desc = parse_text_node(l2_xml)
            else:
                self._logger.warning(f'Unexpected tag for {xml_root.tag}: {elem.tag}')
        if name is None or length is None:  # All signals don't have IV constant Ref or DatatypeRef
            self._logger.error(f'Failed to parse {xml_root.tag}')
            return None
        return SystemSignal(name, data_type_ref, init_value_ref, length, desc, parent)

    def parse_system_signal_group(self, xml_root: Element, parent: ArObject | None) -> SystemSignalGroup | None:
        name = None
        system_signal_refs = None
        for elem in xml_root.findall('./*'):
            if elem.tag == 'SHORT-NAME':
                name = parse_text_node(elem)
            elif elem.tag == 'SYSTEM-SIGNAL-REFS':
                system_signal_refs = []
                for child_elem in elem.findall('./*'):
                    if child_elem.tag != 'SYSTEM-SIGNAL-REF':
                        self._logger.error(f'Unexpected tag for {elem.tag}: {child_elem.tag}')
                        continue
                    system_signal_refs.append(parse_text_node(child_elem))
            else:
                self._logger.warning(f'Unexpected tag for {xml_root.tag}: {elem.tag}')
        if name is None or system_signal_refs is None:
            self._logger.error(f'Failed to parse {xml_root.tag}')
            return None
        return SystemSignalGroup(name, system_signal_refs, parent)

    def parse_system_signal_ar4(self, xml_root: Element, parent: ArObject | None) -> SystemSignal | None:
        """
        parses <SYSTEM-SIGNAL>
        """
        assert (xml_root.tag == 'SYSTEM-SIGNAL')
        name = None
        data_type_ref = None
        init_value_ref = None
        length = None
        dynamic_length = False
        desc = None
        for elem in xml_root.findall('./*'):
            if elem.tag == 'SHORT-NAME':
                name = parse_text_node(elem)
            elif elem.tag == 'DATA-TYPE-REF':
                data_type_ref = parse_text_node(elem)
            elif elem.tag == 'INIT-VALUE-REF':
                init_value_ref = parse_text_node(elem)
            elif elem.tag == 'LENGTH':
                length = parse_int_node(elem)
            elif elem.tag == 'DYNAMIC-LENGTH':
                dynamic_length = self.parse_boolean_node(elem)
            elif elem.tag == 'DESC':
                desc = parse_text_node(elem.find('L-2'))
            else:
                self._logger.warning(f'Unexpected tag for {xml_root.tag}: {elem.tag}')
        if name is None:  # All signals don't have IV constant Ref or DatatypeRef
            self._logger.error(f'Failed to parse {xml_root.tag}')
            return None
        return SystemSignal(name, data_type_ref, init_value_ref, length, dynamic_length, desc, parent)

    def parse_i_signal(self, xml_elem: Element, parent: ArObject | None) -> ISignal | None:
        name = None
        data_transformations = []
        data_type_policy = None
        length = None
        system_signal_ref = None
        transformation_props = []
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(child_elem)
                case 'DATA-TRANSFORMATIONS':
                    for sub_elem in child_elem.findall('./*'):
                        if sub_elem.tag != 'DATA-TRANSFORMATION-REF-CONDITIONAL':
                            self._logger.error(f'Unexpected tag for {child_elem.tag}: {sub_elem.tag}')
                            continue
                        ref_elem = sub_elem.find('DATA-TRANSFORMATION-REF')
                        if ref_elem is None:
                            self._logger.error(f'Missing <DATA-TRANSFORMATION-REF> for {sub_elem.tag}')
                            continue
                        data_transformation = self.parse_text_node(ref_elem)
                        if data_transformation is not None:
                            data_transformations.append(data_transformation)
                case 'DATA-TYPE-POLICY':
                    data_type_policy = self.parse_text_node(child_elem)
                case 'LENGTH':
                    length = self.parse_int_node(child_elem)
                case 'SYSTEM-SIGNAL-REF':
                    system_signal_ref = self.parse_text_node(child_elem)
                case 'TRANSFORMATION-I-SIGNAL-PROPSS':
                    transformation_props = self._parse_element_list(child_elem, {
                        'SOMEIP-TRANSFORMATION-I-SIGNAL-PROPS': self._parse_some_ip_transformation_props,
                        'END-TO-END-TRANSFORMATION-I-SIGNAL-PROPS': self._parse_end_to_end_transformation_props,
                    })
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        if name is None:
            return None
        signal = ISignal(
            name=name,
            data_type_policy=data_type_policy,
            length=length,
            system_signal_ref=system_signal_ref,
            data_transformation_refs=data_transformations,
            transformation_i_signal_props=transformation_props,
            parent=parent,
        )
        return signal

    def parse_i_signal_group(self, xml_elem: Element, parent: ArObject | None) -> ISignalGroup | None:
        name = None
        group_transformations = []
        signal_refs = []
        system_signal_group_ref = None
        transformation_props = []
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'SHORT-NAME':
                    name = self.parse_text_node(child_elem)
                case 'COM-BASED-SIGNAL-GROUP-TRANSFORMATIONS':
                    for sub_elem in child_elem.findall('./*'):
                        if sub_elem.tag != 'DATA-TRANSFORMATION-REF-CONDITIONAL':
                            self._logger.error(f'Unexpected tag for {child_elem.tag}: {sub_elem.tag}')
                            continue
                        ref_elem = sub_elem.find('DATA-TRANSFORMATION-REF')
                        if ref_elem is None:
                            self._logger.error(f'Missing <DATA-TRANSFORMATION-REF> for {sub_elem.tag}')
                            continue
                        data_transformation = self.parse_text_node(ref_elem)
                        if data_transformation is not None:
                            group_transformations.append(data_transformation)
                case 'I-SIGNAL-REFS':
                    for sub_elem in child_elem.findall('./*'):
                        if sub_elem.tag != 'I-SIGNAL-REF':
                            self._logger.error(f'Unexpected tag for {child_elem.tag}: {sub_elem.tag}')
                            continue
                        signal_ref = self.parse_text_node(sub_elem)
                        if signal_ref is not None:
                            signal_refs.append(signal_ref)
                case 'SYSTEM-SIGNAL-GROUP-REF':
                    system_signal_group_ref = self.parse_text_node(child_elem)
                case 'TRANSFORMATION-I-SIGNAL-PROPSS':
                    transformation_props = self._parse_element_list(child_elem,{
                        'SOMEIP-TRANSFORMATION-I-SIGNAL-PROPS': self._parse_some_ip_transformation_props,
                        'END-TO-END-TRANSFORMATION-I-SIGNAL-PROPS': self._parse_end_to_end_transformation_props,
                    })
                case _:
                    self._logger.warning(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        if name is None:
            return None
        signal_group = ISignalGroup(
            name=name,
            com_based_signal_group_transformations=group_transformations,
            i_signal_refs=signal_refs,
            system_signal_group_ref=system_signal_group_ref,
            transformation_i_signal_props=transformation_props,
            parent=parent,
        )
        return signal_group

    def _parse_some_ip_transformation_props(self, xml_elem: Element) -> SomeIpTransformationISignalProps | None:
        variants_elem = xml_elem.find('SOMEIP-TRANSFORMATION-I-SIGNAL-PROPS-VARIANTS')
        if variants_elem is None:
            return None
        conditional_elem = variants_elem.find('SOMEIP-TRANSFORMATION-I-SIGNAL-PROPS-CONDITIONAL')
        if conditional_elem is None:
            return None
        transformer_ref = self.parse_text_node(conditional_elem.find('TRANSFORMER-REF'))
        implements_string_holding = self.parse_boolean_node(conditional_elem.find('IMPLEMENTS-SOMEIP-STRING-HANDLING'))
        msg_type = self.parse_text_node(conditional_elem.find('MESSAGE-TYPE'))
        if transformer_ref is None:
            return None
        props = SomeIpTransformationISignalProps(
            transformer_ref=transformer_ref,
            implements_some_ip_string_handling=implements_string_holding,
            message_type=msg_type,
        )
        return props

    def _parse_end_to_end_transformation_props(self, xml_elem: Element) -> EndToEndTransformationISignalProps | None:
        variants_elem = xml_elem.find('END-TO-END-TRANSFORMATION-I-SIGNAL-PROPS-VARIANTS')
        if variants_elem is None:
            return None
        conditional_elem = variants_elem.find('END-TO-END-TRANSFORMATION-I-SIGNAL-PROPS-CONDITIONAL')
        if conditional_elem is None:
            return None
        transformer_ref = self.parse_text_node(conditional_elem.find('TRANSFORMER-REF'))
        length = self.parse_text_node(conditional_elem.find('DATA-LENGTH'))
        data_ids = []
        ids_elem = conditional_elem.find('DATA-IDS')
        for id_elem in ids_elem.findall('./*'):
            if id_elem.tag != 'DATA-ID':
                self._logger.error(f'Unexpected tag for {ids_elem.tag}: {id_elem.tag}')
                continue
            data_id = self.parse_int_node(id_elem)
            if data_id is not None:
                data_ids.append(data_id)
        if transformer_ref is None:
            return None
        props = EndToEndTransformationISignalProps(
            transformer_ref=transformer_ref,
            data_ids=data_ids,
            data_length=length,
        )
        return props
