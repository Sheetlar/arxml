import abc
from collections import deque
from typing import Callable, TypeVar, Generator
from xml.etree.ElementTree import Element

from autosar.model.ar_object import ArObject
from autosar.model.base import (
    AdminData,
    SpecialDataGroup,
    SpecialData,
    SwDataDefProps,
    SwDataDefPropsVariants,
    SwPointerTargetProps,
    SymbolProps,
    ValueSpecification,
    NumericalValueSpecification,
    TextValueSpecification,
    DataFilter,
    Limit,
    IntLimit,
    FloatLimit,
)
from autosar.model.element import DataElement
from autosar.misc import HasLogger

T = TypeVar('T', bound=ArObject)


def _parse_boolean(value: str | None) -> bool | None:
    if isinstance(value, str):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
    return None


class CommonTagsResult:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.admin_data = None
        self.desc = None
        self.desc_attr = None
        self.long_name = None
        self.long_name_attr = None
        self.name = None
        self.category = None

    def reset(self):
        self._reset()


class BaseParser(HasLogger):
    def __init__(self, version: float | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = version
        self.common = deque()

    def push(self):
        self.common.append(CommonTagsResult())

    def pop(self, obj: ArObject | None = None):
        if obj is not None:
            self.apply_desc(obj)
            self.apply_long_name(obj)
        self.common.pop()

    def base_handler(self, xml_elem: Element):
        """
        Alias for defaultHandler
        """
        self.default_handler(xml_elem)

    def default_handler(self, xml_elem: Element):
        """
        A default handler that parses common tags found under most XML elements
        """
        if xml_elem.tag == 'SHORT-NAME':
            self.common[-1].name = self.parse_text_node(xml_elem)
        elif xml_elem.tag == 'ADMIN-DATA':
            self.common[-1].admin_data = self.parse_admin_data_node(xml_elem)
        elif xml_elem.tag == 'CATEGORY':
            self.common[-1].category = self.parse_text_node(xml_elem)
        elif xml_elem.tag == 'DESC':
            self.common[-1].desc, self.common[-1].desc_attr = self.parse_desc_direct(xml_elem)
        elif xml_elem.tag == 'LONG-NAME':
            self.common[-1].long_name, self.common[-1].long_name_attr = self.parse_long_name_direct(xml_elem)

    def apply_desc(self, obj: ArObject):
        if self.common[-1].desc is not None:
            obj.desc = self.common[-1].desc
            obj.desc_attr = self.common[-1].desc_attr

    def apply_long_name(self, obj: ArObject):
        if self.common[-1].long_name is not None:
            obj.long_name = self.common[-1].long_name
            obj.long_name_attr = self.common[-1].long_name_attr

    @property
    def name(self) -> str | None:
        return self.common[-1].name

    @property
    def admin_data(self) -> AdminData | None:
        return self.common[-1].admin_data

    @property
    def category(self) -> str | None:
        return self.common[-1].category

    @property
    def desc(self) -> tuple[str | None, str | None]:
        return self.common[-1].desc, self.common[-1].desc_attr

    def parse_long_name(self, xml_root: Element, elem: ArObject):
        xml_desc = xml_root.find('LONG-NAME')
        if xml_desc is not None:
            l2_xml = xml_desc.find('L-4')
            if l2_xml is not None:
                l2_text = self.parse_text_node(l2_xml)
                l2_attr = l2_xml.attrib['L']
                elem.desc = l2_text
                elem.desc_attr = l2_attr

    def parse_long_name_direct(self, xml_long_name: Element) -> tuple[str | None, str | None]:
        if xml_long_name is None:
            return None, None
        assert (xml_long_name.tag == 'LONG-NAME')
        l2_xml = xml_long_name.find('L-4')
        if l2_xml is not None:
            l2_text = self.parse_text_node(l2_xml)
            l2_attr = l2_xml.attrib['L']
            return l2_text, l2_attr
        return None, None

    def parse_desc(self, xml_root: Element, elem: ArObject):
        xml_desc = xml_root.find('DESC')
        if xml_desc is not None:
            l2_xml = xml_desc.find('L-2')
            if l2_xml is not None:
                l2_text = self.parse_text_node(l2_xml)
                l2_attr = l2_xml.attrib['L']
                elem.desc = l2_text
                elem.desc_attr = l2_attr

    def parse_desc_direct(self, xml_desc: Element) -> tuple[str | None, str | None]:
        if xml_desc is None:
            return None, None
        assert (xml_desc.tag == 'DESC')
        l2_xml = xml_desc.find('L-2')
        if l2_xml is not None:
            l2_text = self.parse_text_node(l2_xml)
            l2_attr = l2_xml.attrib['L']
            return l2_text, l2_attr
        return None, None

    def log_not_implemented(self, parent: Element, child: Element):
        self._logger.warning(f'Parser not implemented: {parent.tag}::{child.tag}')

    def log_unexpected(self, parent: Element, child: Element):
        self._logger.warning(f'Unexpected tag: {child.tag} for {parent.tag}')

    def log_missing_required(self, parent: Element, child_name: str):
        self._logger.error(f'Missing {child_name} in {parent.tag}, ignoring')

    def find_required_tag(self, in_elem: Element, tag_to_find: str):
        if (child := in_elem.find(tag_to_find)) is None:
            self.log_missing_required(in_elem, tag_to_find)
            return None
        return child

    @staticmethod
    def not_none_dict(data: dict) -> dict:
        return {k: v for k, v in data.items() if v is not None}

    @staticmethod
    def get_uuid(xml_elem: Element | None) -> str | None:
        if xml_elem is None:
            return None
        return xml_elem.attrib.get('UUID', None)

    @staticmethod
    def parse_text_node(xml_elem: Element) -> str | None:
        if xml_elem is None:
            return None
        return xml_elem.text

    @staticmethod
    def parse_int_node(xml_elem: Element) -> int | None:
        if xml_elem is None:
            return None
        return int(xml_elem.text) if xml_elem.text is not None else None

    @staticmethod
    def parse_float_node(xml_elem: Element) -> float | None:
        if xml_elem is None:
            return None
        return float(xml_elem.text) if xml_elem.text is not None else None

    @staticmethod
    def parse_boolean_node(xml_elem: Element) -> bool | None:
        if xml_elem is None:
            return None
        return _parse_boolean(xml_elem.text)

    def parse_number_node(self, xml_elem: Element) -> int | float | None:
        def get_int_base() -> int:
            if text_value.startswith('0x'):
                return 16
            if text_value.startswith('0b'):
                return 2
            if text_value.startswith('0'):
                return 8
            return 10

        if xml_elem is None:
            return None
        text_value = self.parse_text_node(xml_elem).lower()
        try:
            return int(text_value, base=get_int_base())
        except ValueError:
            try:
                return float(text_value)
            except ValueError:
                self._logger.warning(f'Cannot parse numeric node {xml_elem.tag}: "{text_value}", value will be None')
                return None

    @staticmethod
    def has_admin_data(xml_root: Element) -> bool:
        return True if xml_root.find('ADMIN-DATA') is not None else False

    def parse_admin_data_node(self, xml_root: Element | None) -> AdminData | None:
        if xml_root is None:
            return None
        assert (xml_root.tag == 'ADMIN-DATA')
        admin_data = AdminData()
        xml_sdgs = xml_root.find('./SDGS')
        if xml_sdgs is not None:
            for xml_elem in xml_sdgs.findall('./SDG'):
                special_data_group = self._parse_special_data_group(xml_elem)
                admin_data.special_data_groups.append(special_data_group)
        return admin_data

    def _parse_special_data_group(self, xml_elem: Element) -> SpecialDataGroup:
        sdg_gid = xml_elem.attrib['GID']
        special_data_group = SpecialDataGroup(sdg_gid)
        for child_elem in xml_elem.findall('./*'):
            if child_elem.tag == 'SD':
                text = child_elem.text
                sd_gid = child_elem.attrib.get('GID')
                special_data_group.sd.append(SpecialData(text, sd_gid))
            elif child_elem.tag == 'SDG':
                child_group = self._parse_special_data_group(child_elem)
                special_data_group.sdg.append(child_group)
            else:
                self.log_unexpected(xml_elem, child_elem)
        return special_data_group

    def parse_value_specification(self, xml_elem: Element) -> ValueSpecification | None:
        return self.parse_subclass_aggregation(xml_elem, {
            'NUMERICAL-VALUE-SPECIFICATION': self._parse_numerical_value_spec,
            'TEXT-VALUE-SPECIFICATION': self._parse_text_value_spec,
        })

    def _parse_numerical_value_spec(self, xml_elem: Element) -> NumericalValueSpecification:
        values = list(map(self.parse_number_node, xml_elem.findall('VALUE')))
        if len(values) == 1:
            values, = values
        return NumericalValueSpecification(
            short_label=self.parse_text_node(xml_elem.find('SHORT-LABEL')),
            value=values,
        )

    def _parse_text_value_spec(self, xml_elem: Element) -> TextValueSpecification:
        return TextValueSpecification(
            short_label=self.parse_text_node(xml_elem.find('SHORT-LABEL')),
            value=self.parse_text_node(xml_elem.find('VALUE')),
        )

    def parse_data_filter(self, xml_elem: Element) -> DataFilter:
        data_filter = DataFilter(
            data_filter_type=self.parse_text_node(xml_elem.find('DATA-FILTER-TYPE')),
            mask=self.parse_int_node(xml_elem.find('MASK')),
            max=self.parse_int_node(xml_elem.find('MAX')),
            min=self.parse_int_node(xml_elem.find('MIN')),
            offset=self.parse_int_node(xml_elem.find('OFFSET')),
            period=self.parse_int_node(xml_elem.find('PERIOD')),
            x=self.parse_int_node(xml_elem.find('X')),
        )
        return data_filter

    def parse_limit(self, xml_elem: Element) -> Limit | None:
        value = self.parse_number_node(xml_elem)
        if value is None:
            return None
        if isinstance(value, int):
            limit = IntLimit(value)
        else:
            limit = FloatLimit(value)
        if (t := xml_elem.attrib.get('INTERVAL-TYPE', None)) is not None:
            limit.interval_type = t
        return limit

    def parse_sw_data_def_props(self, xml_root: Element, parent: ArObject | None = None) -> SwDataDefPropsVariants | None:
        variants_elem = xml_root.find('SW-DATA-DEF-PROPS-VARIANTS')
        if variants_elem is None:
            return None
        variants = []
        for sub_item_xml in variants_elem:
            if sub_item_xml.tag != 'SW-DATA-DEF-PROPS-CONDITIONAL':
                self.log_unexpected(variants_elem, sub_item_xml)
                continue
            variant = self._parse_single_sw_data_def_props(sub_item_xml, parent)
            assert (variant is not None)
            variants.append(variant)
        if len(variants) == 0:
            return None
        return SwDataDefPropsVariants(variants)

    def _parse_single_sw_data_def_props(
            self,
            xml_root,
            parent: ArObject | None = None,
    ) -> SwDataDefProps:
        assert (xml_root.tag == 'SW-DATA-DEF-PROPS-CONDITIONAL')
        base_type_ref = None
        implementation_type_ref = None
        sw_calibration_access = None
        compu_method_ref = None
        data_constraint_ref = None
        sw_pointer_target_props_xml = None
        sw_impl_policy = None
        sw_address_method_ref = None
        sw_record_layout_ref = None
        unit_ref = None
        for xml_item in xml_root.findall('./*'):
            if xml_item.tag == 'BASE-TYPE-REF':
                base_type_ref = self.parse_text_node(xml_item)
            elif xml_item.tag == 'SW-CALIBRATION-ACCESS':
                sw_calibration_access = self.parse_text_node(xml_item)
            elif xml_item.tag == 'COMPU-METHOD-REF':
                compu_method_ref = self.parse_text_node(xml_item)
            elif xml_item.tag == 'DATA-CONSTR-REF':
                data_constraint_ref = self.parse_text_node(xml_item)
            elif xml_item.tag == 'SW-POINTER-TARGET-PROPS':
                sw_pointer_target_props_xml = xml_item
            elif xml_item.tag == 'IMPLEMENTATION-DATA-TYPE-REF':
                implementation_type_ref = self.parse_text_node(xml_item)
            elif xml_item.tag == 'SW-IMPL-POLICY':
                sw_impl_policy = self.parse_text_node(xml_item)
            elif xml_item.tag == 'SW-ADDR-METHOD-REF':
                sw_address_method_ref = self.parse_text_node(xml_item)
            elif xml_item.tag == 'UNIT-REF':
                unit_ref = self.parse_text_node(xml_item)
            elif xml_item.tag == 'SW-RECORD-LAYOUT-REF':
                sw_record_layout_ref = self.parse_text_node(xml_item)
            elif xml_item.tag == 'ADDITIONAL-NATIVE-TYPE-QUALIFIER':
                self.log_not_implemented(xml_root, xml_item)
                pass  # implement later
            elif xml_item.tag == 'SW-CALPRM-AXIS-SET':
                self.log_not_implemented(xml_root, xml_item)
                pass  # implement later
            elif xml_item.tag == 'INVALID-VALUE':
                self.log_not_implemented(xml_root, xml_item)
                pass  # implement later
            elif xml_item.tag == 'SW-TEXT-PROPS':
                self.log_not_implemented(xml_root, xml_item)
                pass  # implement later
            else:
                self.log_unexpected(xml_root, xml_item)
        variant = SwDataDefProps(
            base_type_ref,
            implementation_type_ref,
            sw_address_method_ref,
            sw_calibration_access,
            sw_impl_policy,
            None,
            sw_record_layout_ref,
            compu_method_ref,
            data_constraint_ref,
            unit_ref,
            parent,
        )
        if sw_pointer_target_props_xml is not None:
            variant.sw_pointer_target_props = self.parse_sw_pointer_target_props(
                sw_pointer_target_props_xml,
                variant,
            )
        return variant

    def parse_sw_pointer_target_props(
            self,
            root_xml: Element,
            parent: ArObject | None = None,
    ) -> SwPointerTargetProps:
        assert (root_xml.tag == 'SW-POINTER-TARGET-PROPS')
        props = SwPointerTargetProps()
        for item_xml in root_xml.findall('./*'):
            if item_xml.tag == 'TARGET-CATEGORY':
                props.target_category = self.parse_text_node(item_xml)
            if item_xml.tag == 'SW-DATA-DEF-PROPS':
                props.variants = self.parse_sw_data_def_props(item_xml, parent)
        return props

    def parse_variable_data_prototype(self, xml_root: Element, parent: ArObject | None = None) -> DataElement | None:
        assert (xml_root.tag == 'VARIABLE-DATA-PROTOTYPE')
        type_ref = None
        props_variants = None
        self.push()
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'TYPE-TREF':
                type_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'SW-DATA-DEF-PROPS':
                props_variants = self.parse_sw_data_def_props(xml_elem)
            elif xml_elem.tag == 'INIT-VALUE':
                pass  # Implement later
            else:
                self.default_handler(xml_elem)
        if self.name is None or type_ref is None:
            self._logger.error('SHORT-NAME and TYPE-TREF must not be None')
            self.pop()
            return None
        data_element = DataElement(self.name, type_ref, category=self.category, parent=parent, admin_data=self.admin_data)
        if props_variants is not None and len(props_variants) > 0:
            data_element.set_props(props_variants[0])
        self.pop(data_element)
        return data_element

    def parse_symbol_props(self, xml_root: Element) -> SymbolProps:
        assert (xml_root.tag == 'SYMBOL-PROPS')
        name = None
        symbol = None
        for xml_elem in xml_root.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                name = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'SYMBOL':
                symbol = self.parse_text_node(xml_elem)
            else:
                self.log_unexpected(xml_root, xml_elem)
        return SymbolProps(name, symbol)

    def __repr__(self):
        return self.__class__.__name__

    def parse_variable_element_list(
            self,
            xml_element: Element | None,
            parser_mapper: dict[str, Callable[[Element], T | None]],
    ) -> list[T]:
        if xml_element is None:
            return []
        result = []
        for child_elem in xml_element.findall('./*'):
            if child_elem.tag not in parser_mapper:
                self.log_unexpected(xml_element, child_elem)
                continue
            parse_element = parser_mapper[child_elem.tag]
            parsed = parse_element(child_elem)
            if parsed is not None:
                result.append(parsed)
        return result

    def parse_element_list(
            self,
            xml_element: Element | None,
            parser: Callable[[Element], T | None],
            expected_child_name: str | None = None,
    ) -> list[T]:
        if xml_element is None:
            return []
        result = []
        if expected_child_name is None:
            expected_child_name = xml_element.tag.removesuffix('S')
        for child_elem in xml_element:
            if child_elem.tag != expected_child_name:
                self.log_unexpected(xml_element, child_elem)
                continue
            parsed = parser(child_elem)
            if parsed is not None:
                result.append(parsed)
        return result

    def parse_subclass_aggregation(
            self,
            role_elem: Element | None,
            subclass_parser_map: dict[str, Callable[[Element], T | None]],
    ) -> T | None:
        if role_elem is None:
            return None
        for subclass, parser in subclass_parser_map.items():
            type_elem = role_elem.find(subclass)
            if type_elem is not None:
                return parser(role_elem)
        self._logger.warning(f'None of known subclasses found for {role_elem.tag}')
        return None

    def child_string_nodes(self, xml_element: Element | None, child_name: str | None = None) -> Generator[str, None, None]:
        if xml_element is None:
            return None
        if child_name is None:
            child_name = xml_element.tag.removesuffix('S')
        for child_elem in xml_element.findall(child_name):
            child_txt = self.parse_text_node(child_elem)
            if child_txt is not None:
                yield child_txt

    def variation_child_string_nodes(self, xml_element: Element | None, child_name: str) -> Generator[str, None, None]:
        if xml_element is None:
            return None
        for child_elem in xml_element.findall(f'{child_name}-CONDITIONAL'):
            child_txt = self.parse_text_node(child_elem.find(child_name))
            if child_txt is not None:
                yield child_txt


class ElementParser(BaseParser, abc.ABC):
    common_tags = ('SHORT-NAME', 'DESC', 'LONG-NAME', 'CATEGORY', 'ADMIN-DATA')

    def parse_common_tags(self, xml_elem: Element):
        desc, _ = self.parse_desc_direct(xml_elem.find('DESC'))
        long_name, _ = self.parse_long_name_direct(xml_elem.find('LONG-NAME'))
        common_args = {
            'name': self.parse_text_node(xml_elem.find('SHORT-NAME')),
            'uuid': self.get_uuid(xml_elem),
            'desc': desc,
            'long_name': long_name,
            'category': self.parse_text_node(xml_elem.find('CATEGORY')),
            'admin_data': self.parse_admin_data_node(xml_elem.find('ADMIN-DATA')),
        }
        return self.not_none_dict(common_args)

    @abc.abstractmethod
    def get_supported_tags(self):
        """
        Returns a list of tag-names (strings) that this parser supports.
        A generator returning strings is also OK.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse_element(self, xml_element: Element, parent: ArObject | None = None):
        """
        Invokes the parser

        xmlElem: Element to parse (instance of xml.etree.ElementTree.Element)
        parent: the parent object (usually a package object)
        Should return an object derived from autosar.element.Element
        """
        raise NotImplementedError
