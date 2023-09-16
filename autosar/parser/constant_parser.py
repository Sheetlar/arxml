from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.constant import (
    ValueAR4,
    Constant,
    IntegerValue,
    StringValue,
    BooleanValue,
    RecordValue,
    ArrayValue,
    TextValue,
    NumericalValue,
    ArrayValueAR4,
    ConstantReference,
    ApplicationValue,
    SwValueCont,
    SwAxisCont,
    Value,
)
from autosar.parser.parser_base import ElementParser


class ConstantParser(ElementParser):
    """
    Constant package parser
    """

    def __init__(self, version: float = 3.0):
        super().__init__(version)

    def get_supported_tags(self):
        return ['CONSTANT-SPECIFICATION']

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> Constant | None:
        if xml_element.tag == 'CONSTANT-SPECIFICATION':
            return self.parse_constant_specification(xml_element, parent)
        return None

    def parse_constant_specification(self, xml_elem: Element, parent: ArObject | None = None) -> Constant | None:
        assert (xml_elem.tag == 'CONSTANT-SPECIFICATION')
        xml_value = None
        xml_value_spec = None
        self.push()
        for xml_elem in xml_elem.findall('./*'):
            if self.version < 4.0 and xml_elem.tag == 'VALUE':
                xml_value = xml_elem
            elif self.version >= 4.0 and xml_elem.tag == 'VALUE-SPEC':
                xml_value_spec = xml_elem
            elif xml_elem.tag == 'TYPE-TREF':
                # type_ref = self.parse_text_node(xml_elem)
                pass
            else:
                self.default_handler(xml_elem)

        if self.name is None or (xml_value is None and xml_value_spec is None):
            self.pop()
            return None
        constant = Constant(self.name, parent=parent, admin_data=self.admin_data)
        if xml_value is not None:
            constant.value = self._parse_value_v3(xml_value.find('./*'), constant)
        elif xml_value_spec is not None:
            values = self.parse_value_v4(xml_value_spec, constant)
            if len(values) != 1:
                self._logger.error('A value specification must contain exactly one element')
            else:
                constant.value = values[0]
        self.pop(constant)
        return constant

    def _parse_value_v3(self, xml_value: Element, parent: ArObject) -> Value | None:
        constant_value = None
        xml_name = xml_value.find('SHORT-NAME')
        if xml_name is None:
            return None
        name = xml_name.text
        if xml_value.tag == 'INTEGER-LITERAL':
            type_ref = xml_value.find('./TYPE-TREF').text
            inner_value = xml_value.find('./VALUE').text
            constant_value = IntegerValue(name, type_ref, inner_value, parent)
        elif xml_value.tag == 'STRING-LITERAL':
            type_ref = xml_value.find('./TYPE-TREF').text
            inner_value = xml_value.find('./VALUE').text
            constant_value = StringValue(name, type_ref, inner_value, parent)
        elif xml_value.tag == 'BOOLEAN-LITERAL':
            type_ref = xml_value.find('./TYPE-TREF').text
            inner_value = xml_value.find('./VALUE').text
            constant_value = BooleanValue(name, type_ref, inner_value, parent)
        elif xml_value.tag == 'RECORD-SPECIFICATION' or xml_value.tag == 'ARRAY-SPECIFICATION':
            type_ref = xml_value.find('./TYPE-TREF').text
            if xml_value.tag == 'RECORD-SPECIFICATION':
                constant_value = RecordValue(name, type_ref, parent=parent)
            else:
                constant_value = ArrayValue(name, type_ref, parent=parent)
            for inner_elem in xml_value.findall('./ELEMENTS/*'):
                inner_constant = self._parse_value_v3(inner_elem, constant_value)
                if inner_constant is not None:
                    constant_value.elements.append(inner_constant)
        return constant_value

    def parse_value_v4(self, xml_value: Element, parent: ArObject | None) -> list[ValueAR4]:
        result = []
        for xml_elem in xml_value.findall('./*'):
            if xml_elem.tag == 'TEXT-VALUE-SPECIFICATION':
                value = self._parse_text_value_specification(xml_elem, parent)
                if value is not None:
                    result.append(value)
            elif xml_elem.tag == 'RECORD-VALUE-SPECIFICATION':
                value = self._parse_record_value_specification(xml_elem, parent)
                if value is not None:
                    result.append(value)
            elif xml_elem.tag == 'NUMERICAL-VALUE-SPECIFICATION':
                value = self._parse_numerical_value_specification(xml_elem, parent)
                if value is not None:
                    result.append(value)
            elif xml_elem.tag == 'ARRAY-VALUE-SPECIFICATION':
                value = self._parse_array_value_specification(xml_elem, parent)
                if value is not None:
                    result.append(value)
            elif xml_elem.tag == 'CONSTANT-REFERENCE':
                value = self._parse_constant_reference(xml_elem, parent)
                if value is not None:
                    result.append(value)
            elif xml_elem.tag == 'APPLICATION-VALUE-SPECIFICATION':
                value = self._parse_application_value_specification(xml_elem, parent)
                if value is not None:
                    result.append(value)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        return result

    def _parse_text_value_specification(self, xml_value: Element, parent: ArObject) -> TextValue | None:
        label = None
        value = None
        for xml_elem in xml_value.findall('./*'):
            if xml_elem.tag == 'SHORT-LABEL':
                label = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'VALUE':
                value = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if value is None:
            self._logger.error('Value must not be None')
            return None
        return TextValue(label, value, parent=parent)

    def _parse_numerical_value_specification(self, xml_value: Element, parent: ArObject) -> NumericalValue | None:
        label = None
        value = None
        for xml_elem in xml_value.findall('./*'):
            if xml_elem.tag == 'SHORT-LABEL':
                label = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'VALUE':
                value = self.parse_number_node(xml_elem)
            else:
                raise NotImplementedError(xml_elem.tag)

        if value is None:
            self._logger.error('Value must not be None')
            return None
        return NumericalValue(label, value, parent=parent)

    def _parse_record_value_specification(self, xml_value: Element, parent: ArObject) -> RecordValue | None:
        label = None
        xml_fields = None
        for xml_elem in xml_value.findall('./*'):
            if xml_elem.tag == 'SHORT-LABEL':
                label = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'FIELDS':
                xml_fields = xml_elem
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if xml_fields is None:
            self._logger.error('<FIELDS> must not be None')
            return None
        record = RecordValue(label, parent=parent)
        record.elements = self.parse_value_v4(xml_fields, record)
        return record

    def _parse_array_value_specification(self, xml_value: Element, parent: ArObject) -> ArrayValueAR4 | None:
        label = None
        xml_elements = None
        for xml_elem in xml_value.findall('./*'):
            if xml_elem.tag == 'SHORT-LABEL':
                label = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'ELEMENTS':
                xml_elements = xml_elem
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if xml_elements is None:
            self._logger.error('<ELEMENTS> must not be None')
            return None
        array = ArrayValueAR4(label, parent=parent)
        array.elements = self.parse_value_v4(xml_elements, array)
        return array

    def _parse_constant_reference(self, xml_root: Element, parent: ArObject):
        label = None
        constant_ref = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SHORT-LABEL':
                label = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'CONSTANT-REF':
                constant_ref = self.parse_text_node(xml_elem)
            else:
                self.base_handler(xml_elem)
        if constant_ref is None:
            self._logger.error('<CONSTANT-REF> must not be None')
            self.pop()
            return None
        obj = ConstantReference(label, constant_ref, parent=parent, admin_data=self.admin_data)
        self.pop(obj)
        return obj

    def _parse_application_value_specification(self, xml_root: Element, parent: ArObject):
        label = None
        sw_value_cont = None
        sw_axis_cont = None
        category = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SHORT-LABEL':
                label = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'CATEGORY':
                category = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'SW-VALUE-CONT':
                sw_value_cont = self._parse_sw_value_cont(xml_elem)
            elif xml_elem.tag == 'SW-AXIS-CONTS':
                xml_child = xml_elem.find('./SW-AXIS-CONT')
                if xml_child is not None:
                    sw_axis_cont = self._parse_sw_axis_cont(xml_child)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        value = ApplicationValue(label, sw_value_cont=sw_value_cont, sw_axis_cont=sw_axis_cont, category=category, parent=parent)
        return value

    def _parse_sw_value_cont(self, xml_root: Element) -> SwValueCont:
        unit_ref = None
        value_list = []
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'UNIT-REF':
                unit_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'SW-VALUES-PHYS':
                for xml_child in xml_elem.findall('./*'):
                    if (xml_child.tag == 'V') or (xml_child.tag == 'VF'):
                        value_list.append(self.parse_number_node(xml_child))
                    elif xml_child.tag == 'VT':
                        value_list.append(self.parse_text_node(xml_child))
                    else:
                        self._logger.warning(f'Unexpected tag: {xml_child.tag}')
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if len(value_list) == 0:
            value_list = None
        return SwValueCont(value_list, unit_ref)

    def _parse_sw_axis_cont(self, xml_root: Element) -> SwAxisCont:
        unit_ref = None
        value_list = []
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'UNIT-REF':
                unit_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'SW-VALUES-PHYS':
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag == 'V':
                        value_list.append(self.parse_number_node(xml_child))
                    else:
                        self._logger.warning(f'Unexpected tag: {xml_child.tag}')
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if len(value_list) == 0:
            value_list = None
        return SwAxisCont(value_list, unit_ref)
