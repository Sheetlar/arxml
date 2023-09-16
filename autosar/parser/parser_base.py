import abc
from collections import deque
from typing import Callable, TypeVar
from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.base import (
    AdminData,
    SpecialDataGroup,
    SpecialData,
    SwDataDefPropsConditional,
    SwPointerTargetProps,
    SymbolProps,
)
from autosar.element import DataElement
from autosar.has_logger import HasLogger

T = TypeVar('T')


def _parse_boolean(value: str | None) -> bool | None:
    if isinstance(value, str):
        if value == 'true':
            return True
        elif value == 'false':
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
        else:
            self._logger.warning(f'Unexpected tag: {xml_elem.tag}')

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
            return False
        return _parse_boolean(xml_elem.text)

    def parse_number_node(self, xml_elem: Element) -> int | float | str | None:
        if xml_elem is None:
            return None
        text_value = self.parse_text_node(xml_elem)
        try:
            retval = int(text_value)
        except ValueError:
            try:
                retval = float(text_value)
            except ValueError:
                retval = text_value
        return retval

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
                self._logger.error(f'Unexpected tag for {xml_elem.tag}: {child_elem.tag}')
        return special_data_group

    def parse_sw_data_def_props(self, xml_root: Element, parent: ArObject | None = None) -> list | None:
        assert (xml_root.tag == 'SW-DATA-DEF-PROPS')
        variants = []
        for item_xml in xml_root.findall('./*'):
            if item_xml.tag != 'SW-DATA-DEF-PROPS-VARIANTS':
                self._logger.error(f'Unexpected tag: {item_xml.tag}')
                continue
            for sub_item_xml in item_xml.findall('./*'):
                if sub_item_xml.tag != 'SW-DATA-DEF-PROPS-CONDITIONAL':
                    self._logger.error(f'Unexpected tag: {sub_item_xml.tag}')
                    continue
                variant = self.parse_sw_data_def_props_conditional(sub_item_xml, parent)
                assert (variant is not None)
                variants.append(variant)
        return variants if len(variants) > 0 else None

    def parse_sw_data_def_props_conditional(
            self,
            xml_root,
            parent: ArObject | None = None,
    ) -> SwDataDefPropsConditional:
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
                self._logger.warning(f'Unhandled: {xml_item.tag}')
                pass  # implement later
            elif xml_item.tag == 'SW-CALPRM-AXIS-SET':
                self._logger.warning(f'Unhandled: {xml_item.tag}')
                pass  # implement later
            elif xml_item.tag == 'INVALID-VALUE':
                self._logger.warning(f'Unhandled: {xml_item.tag}')
                pass  # implement later
            elif xml_item.tag == 'SW-TEXT-PROPS':
                self._logger.warning(f'Unhandled: {xml_item.tag}')
                pass  # implement later
            else:
                self._logger.warning(f'Unexpected tag: {xml_item.tag}')
        variant = SwDataDefPropsConditional(
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
                self._logger.warning(f'Unexpected tag: {xml_elem.tag}')
        return SymbolProps(name, symbol)

    def __repr__(self):
        return self.__class__.__name__

    def _parse_element_list(
            self,
            xml_element: Element,
            parser_mapper: dict[str, Callable[[Element], T | None]],
    ) -> list[T]:
        result = []
        for child_elem in xml_element.findall('./*'):
            if child_elem.tag not in parser_mapper:
                self._logger.error(f'Unexpected tag for {xml_element.tag}: {child_elem.tag}')
                continue
            parse_element = parser_mapper[child_elem.tag]
            parsed = parse_element(child_elem)
            if parsed is not None:
                result.append(parsed)
        return result


class ElementParser(BaseParser, abc.ABC):
    common_tags = ('SHORT-NAME', 'DESC', 'LONG-NAME', 'CATEGORY', 'ADMIN-DATA')

    def _parse_common_tags(self, xml_elem: Element):
        desc, _ = self.parse_desc_direct(xml_elem.find('DESC'))
        long_name, _ = self.parse_long_name_direct(xml_elem.find('LONG-NAME'))
        common_args = {
            'name': self.parse_text_node(xml_elem.find('SHORT-NAME')),
            'desc': desc,
            'long_name': long_name,
            'category': self.parse_text_node(xml_elem.find('CATEGORY')),
            'admin_data': self.parse_admin_data_node(xml_elem.find('ADMIN-DATA')),
        }
        return common_args

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
