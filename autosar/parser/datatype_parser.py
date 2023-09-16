from typing import Callable
from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.datatype import (
    IntegerDataType,
    RecordTypeElement,
    RecordDataType,
    ArrayDataType,
    BooleanDataType,
    StringDataType,
    RealDataType,
    DataConstraint,
    ImplementationDataType,
    ImplementationDataTypeElement,
    SwBaseType,
    DataTypeMappingSet,
    ApplicationPrimitiveDataType,
    ApplicationArrayDataType,
    ApplicationArrayElement,
    ApplicationRecordDataType,
    ApplicationRecordElement,
    DataTypeMap,
    ModeRequestTypeMap,
    CompuMethod,
    Computation,
    CompuScaleElement,
    Unit,
    BufferProperties,
    BufferComputation,
)
from autosar.element import Element as ArElement
from autosar.parser.parser_base import ElementParser


class DataTypeParser(ElementParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 3.0 <= self.version < 4.0:
            self.switcher: dict[str, Callable[[Element, ArObject | None], ArElement | None]] = {
                'ARRAY-TYPE': self.parse_array_type,
                'BOOLEAN-TYPE': self.parse_boolean_type,
                'INTEGER-TYPE': self.parse_integer_type,
                'REAL-TYPE': self.parse_real_type,
                'RECORD-TYPE': self.parse_record_type,
                'STRING-TYPE': self.parse_string_type,
            }
        elif self.version >= 4.0:
            self.switcher: dict[str, Callable[[Element, ArObject | None], ArElement | None]] = {
                'DATA-CONSTR': self.parse_data_constraint,
                'IMPLEMENTATION-DATA-TYPE': self.parse_implementation_data_type,
                'SW-BASE-TYPE': self.parse_sw_base_type,
                'DATA-TYPE-MAPPING-SET': self.parse_data_type_mapping_set,
                'APPLICATION-PRIMITIVE-DATA-TYPE': self.parse_application_primitive_data_type,
                'APPLICATION-ARRAY-DATA-TYPE': self.parse_application_array_data_type,
                'APPLICATION-RECORD-DATA-TYPE': self.parse_application_record_data_type_xml,
            }

    def get_supported_tags(self):
        return self.switcher.keys()

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> ArElement | None:
        parse_func = self.switcher.get(xml_element.tag)
        if parse_func is not None:
            return parse_func(xml_element, parent)
        return None

    def parse_integer_type(self, root: Element, parent: ArObject | None = None) -> IntegerDataType | None:
        if self.version >= 3.0:
            name = root.find("./SHORT-NAME").text
            min_val = int(root.find("./LOWER-LIMIT").text)
            max_val = int(root.find("./UPPER-LIMIT").text)
            data_def_xml = root.find('./SW-DATA-DEF-PROPS')
            data_type = IntegerDataType(name, min_val, max_val, parent=parent)
            self.parse_desc(root, data_type)
            if data_def_xml is not None:
                for elem in data_def_xml.findall('./*'):
                    if elem.tag != 'COMPU-METHOD-REF':
                        self._logger.error(f'Unexpected tag: {elem.tag}')
                        continue
                    data_type.compu_method_ref = self.parse_text_node(elem)
            return data_type

    def parse_record_type(self, root: Element, parent: ArObject | None = None) -> RecordDataType | None:
        if self.version >= 3.0:
            elements = []
            name = root.find("./SHORT-NAME").text
            for elem in root.findall('./ELEMENTS/RECORD-ELEMENT'):
                elem_name = self.parse_text_node(elem.find("./SHORT-NAME"))
                elem_type_ref = self.parse_text_node(elem.find("./TYPE-TREF"))
                elements.append(RecordTypeElement(elem_name, elem_type_ref))
            data_type = RecordDataType(name, elements, parent)
            self.parse_desc(root, data_type)
            return data_type

    def parse_array_type(self, root: Element, parent: ArObject | None = None) -> ArrayDataType | None:
        if self.version >= 3.0:
            name = root.find("./SHORT-NAME").text
            length = int(root.find('ELEMENT/MAX-NUMBER-OF-ELEMENTS').text)
            type_ref = root.find('ELEMENT/TYPE-TREF').text
            data_type = ArrayDataType(name, type_ref, length, parent)
            self.parse_desc(root, data_type)
            return data_type

    def parse_boolean_type(self, root: Element, parent: ArObject | None = None) -> BooleanDataType | None:
        if self.version >= 3:
            name = root.find("./SHORT-NAME").text
            data_type = BooleanDataType(name, parent)
            self.parse_desc(root, data_type)
            return data_type

    def parse_string_type(self, root: Element, parent: ArObject | None = None) -> StringDataType | None:
        if self.version >= 3.0:
            name = root.find("./SHORT-NAME").text
            length = int(root.find('MAX-NUMBER-OF-CHARS').text)
            encoding = root.find('ENCODING').text
            data_type = StringDataType(name, length, encoding, parent)
            self.parse_desc(root, data_type)
            return data_type

    def parse_real_type(self, root: Element, parent: ArObject | None = None) -> RealDataType | None:
        if self.version >= 3.0:
            min_val = None
            min_val_type = 'CLOSED'
            max_val = None
            max_val_type = 'CLOSED'
            name = root.find("./SHORT-NAME").text
            elem = root.find("./LOWER-LIMIT")
            if elem is not None:
                min_val = elem.text
                min_val_type = elem.attrib['INTERVAL-TYPE']
            elem = root.find("./UPPER-LIMIT")
            if elem is not None:
                max_val = elem.text
                max_val_type = elem.attrib['INTERVAL-TYPE']
            has_nan = self.parse_boolean_node(root.find("./ALLOW-NAN"))
            encoding = self.parse_text_node(root.find("./ENCODING"))
            data_type = RealDataType(name, min_val, max_val, min_val_type, max_val_type, has_nan, encoding, parent)
            self.parse_desc(root, data_type)
            return data_type

    def parse_data_constraint(self, xml_root: Element, parent: ArObject | None = None) -> DataConstraint:
        assert (xml_root.tag == 'DATA-CONSTR')
        rules = []
        constraint_level = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'DATA-CONSTR-RULES':
                for xml_child_elem in xml_elem.findall('./DATA-CONSTR-RULE/*'):
                    if xml_child_elem.tag == 'INTERNAL-CONSTRS':
                        rules.append(self._parse_data_constraint_rule(xml_child_elem, 'internalConstraint'))
                    elif xml_child_elem.tag == 'PHYS-CONSTRS':
                        rules.append(self._parse_data_constraint_rule(xml_child_elem, 'physicalConstraint'))
                    elif xml_child_elem.tag == 'CONSTR-LEVEL':
                        constraint_level = self.parse_int_node(xml_child_elem)
                    else:
                        self._logger.warning(f'Unexpected tag: {xml_child_elem.tag}')
            else:
                self.default_handler(xml_elem)
        elem = DataConstraint(self.name, rules, constraint_level, parent, self.admin_data)
        self.pop(elem)
        return elem

    def _parse_data_constraint_rule(
            self,
            xml_elem: Element,
            constraint_type: str,
    ) -> dict[str, int | float | str | None]:
        lower_limit_xml = xml_elem.find('./LOWER-LIMIT')
        upper_limit_xml = xml_elem.find('./UPPER-LIMIT')
        lower_limit = None if lower_limit_xml is None else self.parse_number_node(lower_limit_xml)
        upper_limit = None if upper_limit_xml is None else self.parse_number_node(upper_limit_xml)
        lower_limit_type = 'CLOSED'
        upper_limit_type = 'CLOSED'
        key = 'INTERVAL-TYPE'
        if lower_limit_xml is not None and key in lower_limit_xml.attrib and lower_limit_xml.attrib[key] == 'OPEN':
            lower_limit_type = 'OPEN'
        if upper_limit_xml is not None and key in upper_limit_xml.attrib and upper_limit_xml.attrib[key] == 'OPEN':
            upper_limit_type = 'OPEN'
        return {
            'type': constraint_type,
            'lowerLimit': lower_limit,
            'upperLimit': upper_limit,
            'lowerLimitType': lower_limit_type,
            'upperLimitType': upper_limit_type,
        }

    def parse_implementation_data_type(self, xml_root: Element, parent: ArObject | None = None) -> ImplementationDataType:
        assert (xml_root.tag == 'IMPLEMENTATION-DATA-TYPE')
        variant_props = None
        type_emitter = None
        dynamic_array_size_profile = None
        sub_elements_xml = None
        symbol_props = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SW-DATA-DEF-PROPS':
                variant_props = self.parse_sw_data_def_props(xml_elem)
            elif xml_elem.tag == 'TYPE-EMITTER':
                type_emitter = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'DYNAMIC-ARRAY-SIZE-PROFILE':
                dynamic_array_size_profile = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'SUB-ELEMENTS':
                sub_elements_xml = xml_elem
            elif xml_elem.tag == 'SYMBOL-PROPS':
                symbol_props = self.parse_symbol_props(xml_elem)
            else:
                self.default_handler(xml_elem)
        data_type = ImplementationDataType(
            self.name,
            variant_props=variant_props,
            dynamic_array_size_profile=dynamic_array_size_profile,
            type_emitter=type_emitter,
            category=self.category,
            parent=parent,
            admin_data=self.admin_data
        )
        if sub_elements_xml is not None:
            data_type.sub_elements = self.parse_implementation_data_type_sub_elements(
                sub_elements_xml,
                data_type,
            )
        if symbol_props is not None:
            data_type.symbol_props = symbol_props
        self.pop(data_type)
        return data_type

    def parse_implementation_data_type_sub_elements(
            self,
            xml_root: Element,
            parent: ArObject,
    ) -> list[ImplementationDataTypeElement]:
        assert (xml_root.tag == 'SUB-ELEMENTS')
        elements = []
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag != 'IMPLEMENTATION-DATA-TYPE-ELEMENT':
                self._logger.error(f'Unexpected tag: {xml_elem.tag}')
                continue
            elements.append(self.parse_implementation_data_type_element(xml_elem, parent))
        return elements

    def parse_implementation_data_type_element(
            self,
            xml_root: Element,
            parent: ArObject,
    ) -> ImplementationDataTypeElement:
        assert (xml_root.tag == 'IMPLEMENTATION-DATA-TYPE-ELEMENT')
        array_size = None
        array_size_semantics = None
        variants = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SW-DATA-DEF-PROPS':
                variants = self.parse_sw_data_def_props(xml_elem)
            elif xml_elem.tag == 'ARRAY-SIZE':
                array_size = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'ARRAY-SIZE-SEMANTICS':
                array_size_semantics = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'SUB-ELEMENTS':
                pass  # implement later
            else:
                self.default_handler(xml_elem)
        elem = ImplementationDataTypeElement(
            self.name,
            self.category,
            array_size,
            array_size_semantics,
            variants,
            parent,
            self.admin_data,
        )
        self.pop(elem)
        return elem

    def parse_sw_base_type(self, xml_root: Element, parent: ArObject | None = None) -> SwBaseType:
        assert (xml_root.tag == 'SW-BASE-TYPE')
        base_type_size = None
        base_type_encoding = None
        native_declaration = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'BASE-TYPE-SIZE':
                base_type_size = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'BASE-TYPE-ENCODING':
                base_type_encoding = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'NATIVE-DECLARATION':
                native_declaration = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'MEM-ALIGNMENT':
                pass  # implement later
            elif xml_elem.tag == 'BYTE-ORDER':
                pass  # implement later
            else:
                self.default_handler(xml_elem)
        elem = SwBaseType(
            self.name,
            base_type_size,
            base_type_encoding,
            native_declaration,
            self.category,
            parent,
            self.admin_data,
        )
        self.pop(elem)
        return elem

    def parse_data_type_mapping_set(
            self,
            xml_root: Element,
            parent: ArObject | None = None,
    ) -> DataTypeMappingSet | None:
        assert (xml_root.tag == 'DATA-TYPE-MAPPING-SET')
        name = None
        admin_data = None
        data_type_maps = []
        mode_request_type_maps = []
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'ADMIN-DATA':
                admin_data = self.parse_admin_data_node(xml_elem)
            elif xml_elem.tag == 'SHORT-NAME':
                name = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'DATA-TYPE-MAPS':
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag != 'DATA-TYPE-MAP':
                        self._logger.error(f'Unexpected tag: {xml_child.tag}')
                        continue
                    data_type_map = self._parse_data_type_map_xml(xml_child)
                    assert (data_type_map is not None)
                    data_type_maps.append(data_type_map)
            elif xml_elem.tag == 'MODE-REQUEST-TYPE-MAPS':
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag != 'MODE-REQUEST-TYPE-MAP':
                        self._logger.error(f'Unexpected tag: {xml_elem.tag}')
                        continue
                    mode_request_type_map = self._parse_mode_request_type_map_xml(xml_child)
                    assert (mode_request_type_map is not None)
                    mode_request_type_maps.append(mode_request_type_map)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        if name is None:
            self._logger.error('SHORT-NAME cannot be None')
            return None
        elem = DataTypeMappingSet(name, parent, admin_data)
        for mapping in [*data_type_maps, *mode_request_type_maps]:
            elem.add(mapping)
        return elem

    def parse_application_primitive_data_type(
            self,
            xml_root: Element,
            parent: ArObject | None = None,
    ) -> ApplicationPrimitiveDataType:
        assert (xml_root.tag == 'APPLICATION-PRIMITIVE-DATA-TYPE')
        variant_props = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SW-DATA-DEF-PROPS':
                variant_props = self.parse_sw_data_def_props(xml_elem)
            else:
                self.default_handler(xml_elem)
        if self.name is None:
            self._logger.error('SHORT-NAME cannot be None')
        elem = ApplicationPrimitiveDataType(self.name, variant_props, self.category, parent, self.admin_data)
        self.pop(elem)
        return elem

    def parse_application_array_data_type(
            self,
            xml_root: Element,
            parent: ArObject | None = None,
    ) -> ApplicationArrayDataType:
        assert (xml_root.tag == 'APPLICATION-ARRAY-DATA-TYPE')
        element = None
        variant_props = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'ELEMENT':
                element = self.parse_application_array_element(xml_elem)
            elif xml_elem.tag == 'SW-DATA-DEF-PROPS':
                variant_props = self.parse_sw_data_def_props(xml_elem)
            elif xml_elem.tag == 'DYNAMIC-ARRAY-SIZE-PROFILE':
                pass  # implement later
            else:
                self.default_handler(xml_elem)
        if element is None:
            self._logger.error('No <ELEMENT> object found')
        elem = ApplicationArrayDataType(self.name, element, variant_props, self.category, parent, self.admin_data)
        self.pop(elem)
        return elem

    def parse_application_array_element(self, xml_root: Element) -> ApplicationArrayElement:
        assert (xml_root.tag == 'ELEMENT')
        type_ref = None
        array_size = None
        size_handling = None
        size_semantics = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'TYPE-TREF':
                type_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'ARRAY-SIZE-HANDLING':
                size_handling = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'ARRAY-SIZE-SEMANTICS':
                size_semantics = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'MAX-NUMBER-OF-ELEMENTS':
                array_size = self.parse_text_node(xml_elem)
            else:
                self.default_handler(xml_elem)
        elem = ApplicationArrayElement(
            self.name,
            type_ref,
            array_size,
            size_handling,
            size_semantics,
            self.category,
            admin_data=self.admin_data,
        )
        self.pop(elem)
        return elem

    def parse_application_record_data_type_xml(
            self,
            xml_root: Element,
            parent: ArObject | None = None,
    ) -> ApplicationRecordDataType:
        assert (xml_root.tag == 'APPLICATION-RECORD-DATA-TYPE')
        elements_xml = None
        variant_props = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'ELEMENTS':
                elements_xml = xml_elem
            elif xml_elem.tag == 'SW-DATA-DEF-PROPS':
                variant_props = self.parse_sw_data_def_props(xml_elem)
            else:
                self.default_handler(xml_elem)
        elem = ApplicationRecordDataType(self.name, None, variant_props, self.category, parent, self.admin_data)
        if elements_xml is not None:
            for xml_child in elements_xml.findall('./'):
                if xml_child.tag != 'APPLICATION-RECORD-ELEMENT':
                    self._logger.error(f'Unexpected tag: {xml_child.tag}')
                    continue
                elem.elements.append(self._parse_application_record_element_xml(xml_child, parent=elem))
        self.pop(elem)
        return elem

    def _parse_application_record_element_xml(self, xml_root: Element, parent: ArObject) -> ApplicationRecordElement:
        assert (xml_root.tag == 'APPLICATION-RECORD-ELEMENT')
        type_ref = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'TYPE-TREF':
                type_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'SW-DATA-DEF-PROPS':
                # variant_props = self.parse_sw_data_def_props(xml_elem)
                pass
            else:
                self.default_handler(xml_elem)
        elem = ApplicationRecordElement(self.name, type_ref, self.category, parent, self.admin_data)
        self.pop(elem)
        return elem

    def _parse_data_type_map_xml(self, xml_root: Element) -> DataTypeMap:
        assert (xml_root.tag == 'DATA-TYPE-MAP')
        application_data_type_ref = None
        implementation_data_type_ref = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'APPLICATION-DATA-TYPE-REF':
                application_data_type_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'IMPLEMENTATION-DATA-TYPE-REF':
                implementation_data_type_ref = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        return DataTypeMap(application_data_type_ref, implementation_data_type_ref)

    def _parse_mode_request_type_map_xml(self, xml_root: Element) -> ModeRequestTypeMap:
        assert (xml_root.tag == 'MODE-REQUEST-TYPE-MAP')
        mode_declaration_group_ref = None
        implementation_data_type_ref = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'MODE-GROUP-REF':
                mode_declaration_group_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'IMPLEMENTATION-DATA-TYPE-REF':
                implementation_data_type_ref = self.parse_text_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        return ModeRequestTypeMap(mode_declaration_group_ref, implementation_data_type_ref)


class DataTypeSemanticsParser(ElementParser):
    def get_supported_tags(self):
        return ['COMPU-METHOD']

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> CompuMethod | None:
        if xml_element.tag == 'COMPU-METHOD':
            return self._parse_compu_method_xml(xml_element, parent)
        return None

    def _parse_compu_method_xml(self, xml_root: Element, parent: ArObject | None = None) -> CompuMethod:
        assert (xml_root.tag == 'COMPU-METHOD')
        compu_internal_to_phys = None
        compu_phys_to_internal = None
        unit_ref = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'COMPU-INTERNAL-TO-PHYS':
                compu_internal_to_phys = self._parse_computation_xml(xml_elem)
                assert (compu_internal_to_phys is not None)
            elif xml_elem.tag == 'COMPU-PHYS-TO-INTERNAL':
                compu_phys_to_internal = self._parse_computation_xml(xml_elem)
                assert (compu_phys_to_internal is not None)
            elif xml_elem.tag == 'UNIT-REF':
                unit_ref = self.parse_text_node(xml_elem)
            else:
                self.default_handler(xml_elem)
        compu_method = CompuMethod(
            self.name,
            False,
            False,
            unit_ref,
            self.category,
            parent,
            self.admin_data,
        )
        self.pop(compu_method)
        if compu_internal_to_phys is not None:
            compu_method.int_to_phys = compu_internal_to_phys
        if compu_phys_to_internal is not None:
            compu_method.phys_to_int = compu_phys_to_internal
        return compu_method

    def _parse_computation_xml(self, xml_root: Element) -> Computation:
        assert (xml_root.tag == 'COMPU-INTERNAL-TO-PHYS') or (xml_root.tag == 'COMPU-PHYS-TO-INTERNAL')
        computation = Computation()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'COMPU-SCALES':
                for compu_scale_xml in xml_elem.findall('COMPU-SCALE'):
                    compu_scale = self._parse_compu_scale_xml(compu_scale_xml)
                    computation.elements.append(compu_scale)
            elif xml_elem.tag == 'COMPU-DEFAULT-VALUE':
                for xml_child in xml_elem.findall('./*'):
                    if xml_child.tag == 'V':
                        computation.default_value = self.parse_number_node(xml_child)
                        break
                    elif xml_child.tag == 'VT':
                        computation.default_value = self.parse_text_node(xml_child)
                        break
                    elif xml_child.tag == 'VF':
                        computation.default_value = self.parse_number_node(xml_child)
                        break
                    else:
                        self._logger.warning(f'Unexpected tag: {xml_child.tag}')
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        return computation

    def _parse_compu_scale_xml(self, xml_root: Element) -> CompuScaleElement:
        assert (xml_root.tag == 'COMPU-SCALE')
        label = None
        lower_limit = None
        upper_limit = None
        lower_limit_type = None
        upper_limit_type = None
        symbol = None
        admin_data = None
        offset = None
        numerator = None
        denominator = None
        text_value = None
        mask = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'DESC':
                pass  # implement later
            elif xml_elem.tag == 'SHORT-LABEL':
                label = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'LOWER-LIMIT':
                lower_limit = self.parse_number_node(xml_elem)
                if (self.version >= 4.0) and 'INTERVAL-TYPE' in xml_elem.attrib:
                    lower_limit_type = xml_elem.attrib['INTERVAL-TYPE']
            elif xml_elem.tag == 'UPPER-LIMIT':
                upper_limit = self.parse_number_node(xml_elem)
                if (self.version >= 4.0) and 'INTERVAL-TYPE' in xml_elem.attrib:
                    upper_limit_type = xml_elem.attrib['INTERVAL-TYPE']
            elif xml_elem.tag == 'COMPU-RATIONAL-COEFFS':
                offset, numerator, denominator = self._parse_compu_rational_xml(xml_elem)
            elif xml_elem.tag == 'SYMBOL':
                symbol = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'ADMIN-DATA':
                admin_data = self.parse_admin_data_node(xml_elem)
            elif xml_elem.tag == 'COMPU-CONST':
                text_value = self.parse_text_node(xml_elem.find('./VT'))
            elif xml_elem.tag == 'MASK':
                mask = self.parse_int_node(xml_elem)
            else:
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        compu_scale = CompuScaleElement(
            lower_limit,
            upper_limit,
            lower_limit_type,
            upper_limit_type,
            label,
            symbol,
            admin_data,
        )
        compu_scale.offset = offset
        compu_scale.numerator = numerator
        compu_scale.denominator = denominator
        compu_scale.text_value = text_value
        compu_scale.mask = mask
        return compu_scale

    def _parse_compu_rational_xml(
            self,
            xml_root: Element,
    ) -> tuple[int | float | str, int | float | str, int | float | str]:
        assert (xml_root.tag == 'COMPU-RATIONAL-COEFFS')
        num_xml = xml_root.findall('./COMPU-NUMERATOR/V')
        den_xml = xml_root.findall('./COMPU-DENOMINATOR/V')
        assert (num_xml is not None)
        assert (len(num_xml) == 2)
        assert (den_xml is not None)
        if self.parse_text_node(num_xml[0]):
            offset = self.parse_number_node(num_xml[0])
        else:
            offset = 0
        if self.parse_text_node(num_xml[1]):
            numerator = self.parse_number_node(num_xml[1])
        else:
            numerator = 1
        denominator = self.parse_number_node(den_xml[0])
        return offset, numerator, denominator


class DataTypeUnitsParser(ElementParser):
    def get_supported_tags(self):
        return ['UNIT']

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> Unit | None:
        if xml_element.tag == 'UNIT':
            return self._parse_unit(xml_element, parent)
        return None

    def _parse_unit(self, xml_root: Element, parent: ArObject | None = None) -> Unit:
        assert (xml_root.tag == 'UNIT')
        factor = None
        offset = None
        name = self.parse_text_node(xml_root.find("./SHORT-NAME"))
        display_name = self.parse_text_node(xml_root.find("./DISPLAY-NAME"))
        if self.version >= 4.0:
            factor = self.parse_number_node(xml_root.find("./FACTOR-SI-TO-UNIT"))
            offset = self.parse_number_node(xml_root.find("./OFFSET-SI-TO-UNIT"))
        return Unit(name, display_name, factor, offset, parent)


class BufferPropertiesParser(ElementParser):
    def get_supported_tags(self):
        return ['BUFFER-PROPERTIES']

    def parse_element(self, xml_element: Element, *_) -> BufferProperties | None:
        if xml_element.tag == 'BUFFER-PROPERTIES':
            return self._parse_buffer_props(xml_element)
        return None

    def _parse_buffer_props(self, xml_elem: Element) -> BufferProperties:
        computation = None
        header_len = 0
        in_place = False
        for child_elem in xml_elem.findall('./*'):
            match child_elem.tag:
                case 'BUFFER-COMPUTATION':
                    computation = self._parse_buffer_computation(child_elem)
                case 'HEADER-LENGTH':
                    raw_hdr_len = self.parse_int_node(child_elem)
                    if raw_hdr_len is not None:
                        header_len = raw_hdr_len
                case 'IN-PLACE':
                    in_place = self.parse_boolean_node(child_elem)
                case _:
                    self._logger.warning(f'Unexpected tag: {child_elem.tag}')
        props = BufferProperties(
            buffer_computation=computation,
            header_length=header_len,
            in_place=in_place,
        )
        return props

    def _parse_buffer_computation(self, xml_elem: Element) -> BufferComputation:
        try:
            offset_elem, numerator_elem = xml_elem.findall('./COMPU-NUMERATOR/V')
            offset = self.parse_int_node(offset_elem)
            numerator = self.parse_number_node(numerator_elem)
        except ValueError:
            offset = None
            numerator = None
        denominator = self.parse_int_node(xml_elem.find('./COMPU-DENOMINATOR/V'))
        computation = BufferComputation(
            offset=offset,
            numerator=numerator,
            denominator=denominator,
        )
        return computation
