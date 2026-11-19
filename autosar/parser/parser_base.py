from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from functools import wraps
from itertools import chain
from typing import Any, Iterable, Generator, Callable, TypeVar, Generic, Protocol, runtime_checkable
from xml.etree.ElementTree import Element

from autosar.misc import HasLogger, not_none, Skip
from autosar.model.ar_object import ArObject, MaybeArObject
from autosar.model.base import (
    OldAdminData,
    SpecialDataGroup,
    SpecialData,
    SymbolProps,
    DataFilter,
    Limit,
    IntLimit,
    FloatLimit,
    LangStr,
)
from autosar.model.sw_def_props import SwDataDefPropsContent, SwDataDefProps, SwPointerTargetProps
from autosar.model.value_spec import NumericalValueSpecification, TextValueSpecification, ValueSpecification
from autosar.model.element import DataElement
from autosar.model.enums import SomeEnum, IntervalTypeEnum
from autosar.model.languages_enum import LEnum

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
            self.common[-1].name = self._parse_text_node(xml_elem)
        elif xml_elem.tag == 'ADMIN-DATA':
            self.common[-1].admin_data = self.parse_admin_data_node(xml_elem)
        elif xml_elem.tag == 'CATEGORY':
            self.common[-1].category = self._parse_text_node(xml_elem)
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
    def admin_data(self) -> OldAdminData | None:
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
                l2_text = self._parse_text_node(l2_xml)
                l2_attr = l2_xml.attrib['L']
                elem.desc = l2_text
                elem.desc_attr = l2_attr

    def parse_long_name_direct(self, xml_long_name: Element | None) -> tuple[str | None, str | None]:
        if xml_long_name is None:
            return None, None
        assert (xml_long_name.tag == 'LONG-NAME')
        l2_xml = xml_long_name.find('L-4')
        if l2_xml is not None:
            l2_text = self._parse_text_node(l2_xml)
            l2_attr = l2_xml.attrib['L']
            return l2_text, l2_attr
        return None, None

    def parse_desc(self, xml_root: Element, elem: ArObject):
        xml_desc = xml_root.find('DESC')
        if xml_desc is not None:
            l2_xml = xml_desc.find('L-2')
            if l2_xml is not None:
                l2_text = self._parse_text_node(l2_xml)
                l2_attr = l2_xml.attrib['L']
                elem.desc = l2_text
                elem.desc_attr = l2_attr

    def parse_desc_direct(self, xml_desc: Element | None) -> tuple[str | None, str | None]:
        if xml_desc is None:
            return None, None
        assert (xml_desc.tag == 'DESC')
        l2_xml = xml_desc.find('L-2')
        if l2_xml is not None:
            l2_text = self._parse_text_node(l2_xml)
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
    def _parse_text_node(xml_elem: Element | None) -> str | None:
        if xml_elem is None:
            return None
        return xml_elem.text

    def _parse_enum_node(self, xml_elem: Element, enum_type: type[SomeEnum]) -> SomeEnum | None:
        try:
            return enum_type(self._parse_text_node(xml_elem))
        except ValueError:
            return None

    def _parse_int_node(self, xml_elem: Element | None) -> int | None:
        def get_int_base() -> int:
            if text_value.startswith('0x'):
                return 16
            if text_value.startswith('0b'):
                return 2
            if text_value.startswith('0'):
                return 8
            return 10

        text_value = self._parse_text_node(xml_elem)
        if text_value is None:
            return None
        return int(text_value.lower(), base=get_int_base())

    def _parse_float_node(self, xml_elem: Element | None) -> float | None:
        text_value = self._parse_text_node(xml_elem)
        if text_value is None:
            return None
        return float(text_value.lower())

    def _parse_number_node(
            self,
            xml_elem: Element | None,
            log: bool = True,
    ) -> int | float | None:
        if xml_elem is None:
            return None
        try:
            return self._parse_int_node(xml_elem)
        except ValueError:
            try:
                return self._parse_float_node(xml_elem)
            except ValueError:
                if log:
                    self._logger.warning(f'Cannot parse numeric node {xml_elem.tag}: "{self._parse_text_node(xml_elem)}", value will be None')
                return None

    @staticmethod
    def _parse_boolean_node(xml_elem: Element | None) -> bool | None:
        if xml_elem is None:
            return None
        return _parse_boolean(xml_elem.text)

    @staticmethod
    def has_admin_data(xml_root: Element) -> bool:
        return True if xml_root.find('ADMIN-DATA') is not None else False

    def parse_admin_data_node(self, xml_root: Element | None) -> OldAdminData | None:
        if xml_root is None:
            return None
        assert (xml_root.tag == 'ADMIN-DATA')
        admin_data = OldAdminData()
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
        values = list(map(self._parse_number_node, xml_elem.findall('VALUE')))
        if len(values) == 1:
            values, = values
        return NumericalValueSpecification(
            short_label=self._parse_text_node(xml_elem.find('SHORT-LABEL')),
            value=values,
        )

    def _parse_text_value_spec(self, xml_elem: Element) -> TextValueSpecification:
        return TextValueSpecification(
            short_label=self._parse_text_node(xml_elem.find('SHORT-LABEL')),
            value=self._parse_text_node(xml_elem.find('VALUE')),
        )

    def parse_data_filter(self, xml_elem: Element) -> DataFilter:
        data_filter = DataFilter(
            data_filter_type=self._parse_text_node(xml_elem.find('DATA-FILTER-TYPE')),
            mask=self._parse_int_node(xml_elem.find('MASK')),
            max=self._parse_int_node(xml_elem.find('MAX')),
            min=self._parse_int_node(xml_elem.find('MIN')),
            offset=self._parse_int_node(xml_elem.find('OFFSET')),
            period=self._parse_int_node(xml_elem.find('PERIOD')),
            x=self._parse_int_node(xml_elem.find('X')),
        )
        return data_filter

    def _parse_limit(self, xml_elem: Element) -> Limit | None:
        value = self._parse_number_node(xml_elem)
        if value is None:
            return None
        if isinstance(value, int):
            limit = IntLimit(value)
        else:
            limit = FloatLimit(value)
        if (t := xml_elem.attrib.get('INTERVAL-TYPE', None)) is not None:
            try:
                limit.interval_type = IntervalTypeEnum(t)
            except ValueError:
                self._logger.warning(f'Invalid interval type for LIMIT ({t}), CLOSED will be used')
        return limit

    def _parse_lang_string(self, xml_element: Element, *, l_num: int) -> LangStr | None:
        l_element = xml_element.find(f'L-{l_num}')
        raw_value = self._parse_text_node(l_element)
        if raw_value is None:
            return None
        l_element: Element  # If None then raw_value is None
        value = LangStr(raw_value)
        try:
            value.language = LEnum(l_element.attrib['L'])
        except (KeyError, ValueError):
            return None
        return value

    def parse_sw_data_def_props(self, xml_root: Element, parent: ArObject | None = None) -> SwDataDefProps | None:
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
        return SwDataDefProps(variants)

    def _parse_single_sw_data_def_props(
            self,
            xml_root,
            parent: ArObject | None = None,
    ) -> SwDataDefPropsContent:
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
                base_type_ref = self._parse_text_node(xml_item)
            elif xml_item.tag == 'SW-CALIBRATION-ACCESS':
                sw_calibration_access = self._parse_text_node(xml_item)
            elif xml_item.tag == 'COMPU-METHOD-REF':
                compu_method_ref = self._parse_text_node(xml_item)
            elif xml_item.tag == 'DATA-CONSTR-REF':
                data_constraint_ref = self._parse_text_node(xml_item)
            elif xml_item.tag == 'SW-POINTER-TARGET-PROPS':
                sw_pointer_target_props_xml = xml_item
            elif xml_item.tag == 'IMPLEMENTATION-DATA-TYPE-REF':
                implementation_type_ref = self._parse_text_node(xml_item)
            elif xml_item.tag == 'SW-IMPL-POLICY':
                sw_impl_policy = self._parse_text_node(xml_item)
            elif xml_item.tag == 'SW-ADDR-METHOD-REF':
                sw_address_method_ref = self._parse_text_node(xml_item)
            elif xml_item.tag == 'UNIT-REF':
                unit_ref = self._parse_text_node(xml_item)
            elif xml_item.tag == 'SW-RECORD-LAYOUT-REF':
                sw_record_layout_ref = self._parse_text_node(xml_item)
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
        variant = SwDataDefPropsContent(
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
                props.target_category = self._parse_text_node(item_xml)
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
                type_ref = self._parse_text_node(xml_elem)
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
                name = self._parse_text_node(xml_elem)
            elif xml_elem.tag == 'SYMBOL':
                symbol = self._parse_text_node(xml_elem)
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
        if (type_elem := role_elem.find('*')) is None:
            self._logger.warning(f'Role element {role_elem.tag} is empty')
            return None
        try:
            parser = subclass_parser_map[type_elem.tag]
        except KeyError:
            self._logger.warning(f'Unknown subclass {type_elem.tag} found for role {role_elem.tag}')
            return None
        return parser(role_elem)

    def child_string_nodes(self, xml_element: Element | None, child_name: str | None = None) -> Generator[str, None, None]:
        if xml_element is None:
            return
        if child_name is None:
            child_name = xml_element.tag.removesuffix('S')
        for child_elem in xml_element.findall(child_name):
            child_txt = self._parse_text_node(child_elem)
            if child_txt is not None:
                yield child_txt

    def variation_child_string_nodes(self, xml_element: Element | None, child_name: str) -> Generator[str, None, None]:
        if xml_element is None:
            return
        for child_elem in xml_element.findall(f'{child_name}-CONDITIONAL'):
            child_txt = self._parse_text_node(child_elem.find(child_name))
            if child_txt is not None:
                yield child_txt


class ElementParser(BaseParser, ABC):
    common_tags = ('SHORT-NAME', 'DESC', 'LONG-NAME', 'CATEGORY', 'ADMIN-DATA')

    def parse_common_tags(self, xml_elem: Element):
        desc, _ = self.parse_desc_direct(xml_elem.find('DESC'))
        long_name, _ = self.parse_long_name_direct(xml_elem.find('LONG-NAME'))
        common_args = {
            'name': self._parse_text_node(xml_elem.find('SHORT-NAME')),
            'uuid': self.get_uuid(xml_elem),
            'desc': desc,
            'long_name': long_name,
            'category': self._parse_text_node(xml_elem.find('CATEGORY')),
            'admin_data': self.parse_admin_data_node(xml_elem.find('ADMIN-DATA')),
        }
        return self.not_none_dict(common_args)

    @abstractmethod
    def get_supported_tags(self):
        """
        Returns a list of tag-names (strings) that this parser supports.
        A generator returning strings is also OK.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_element(self, xml_element: Element, parent: ArObject | None = None):
        """
        Invokes the parser

        xmlElem: Element to parse (instance of xml.etree.ElementTree.Element)
        parent: the parent object (usually a package object)
        Should return an object derived from autosar.element.Element
        """
        raise NotImplementedError


R = TypeVar('R')


@dataclass
class HandlerSpecs:
    tag: str
    param: str | None
    alt_tags: tuple[str, ...] = ()
    required: bool = False

    @property
    def all_supported_tags(self):
        yield self.tag
        yield from self.alt_tags


@runtime_checkable
class HandlerMethod(Protocol[R]):
    specs: HandlerSpecs

    def __call__(self, xml_element: Element) -> R | None:
        ...


def handler(tag: str, *alt_tags: str, param: str | None = None, required: bool = False):
    """
    Handler definition for the specified tag.
    :param tag: Tag to be handled
    :param alt_tags: Other possible tags that refer to the same element
    :param param: Target class parameter the result should be passed as.
    :param required: Mark the tag as required. If not present an error will be reported.
    :return: Processed element
    """
    def decorator(func: Callable[[Any], R | None]) -> Callable[[Any], R | None]:
        func.specs = HandlerSpecs(tag, param, alt_tags, required)
        return func

    if param is None:
        param = tag.lower().replace('-', '_')
    return decorator


def not_implemented_handler(tag: str, *alt_tags: str):
    """
    Marks a specified tag as not implemented.
    If a not implemented tag is encountered, it will not be reported as an error.
    :param tag: Tag name of the not implemented element
    :param alt_tags: Any other possible tags referring to the same element
    :return: Nothing
    """
    def decorator(func: Callable[[Any], R | None]) -> Callable[[Any], R | None]:
        func.specs = HandlerSpecs(tag, None, alt_tags)
        return func

    return decorator


def skip_return(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        return Skip

    return wrapper


def multiple_with_check(
        direct_func: Callable[[Any, Element], R | None] | None = None,
        /, *,
        expected_name: str | None = None,
):
    """
    Applies the function to all children of the XML element.
    Automatically checks and report children with unexpected tag.
    :param direct_func: Function to be wrapped, if expected_name not provided (default will be used).
    :param expected_name: Expected child element tag, if different from default.
    :return: Filtered (not None) iterable of processed elements.
    """
    def decorator(
            func: Callable[[Any, Element], R | None],
    ) -> Callable[[Any, Element], Iterable[R]]:
        @wraps(func)
        def wrapper(self: BetterParser, xml_element: Element) -> Iterable[R]:
            def apply_handler(child: Element) -> R | None:
                if child.tag != expected_name:
                    if child.tag not in invalid_tags:
                        self._logger.warning(f'Unexpected item {child.tag} in collection {xml_element.tag}')
                        invalid_tags.add(child.tag)
                    return None
                return func(self, child)

            nonlocal expected_name
            if expected_name is None:
                expected_name = xml_element.tag.removesuffix('S')
            invalid_tags = set()
            return filter(not_none, map(apply_handler, xml_element))

        return wrapper

    if direct_func is not None:
        return decorator(direct_func)
    return decorator


def multiple(
        func: Callable[[Any, Element], R | None],
) -> Callable[[Any, Element], Iterable[R]]:
    """
    Applies the function to all children of the XML element.
    If the child element has an unexpected tag, the function should raise NameError.
    :param func: Function to be wrapped.
    :return: Filtered (not None) iterable of processed elements.
    """
    @wraps(func)
    def wrapper(self: BetterParser, xml_element: Element) -> Iterable[R]:
        def apply_handler(child: Element) -> R | None:
            try:
                return func(self, child)
            except NameError:
                if child.tag not in invalid_tags:
                    self._logger.warning(f'Unexpected item {child.tag} in collection {xml_element.tag}')
                    invalid_tags.add(child.tag)
                return None

        invalid_tags = set()
        return filter(not_none, map(apply_handler, xml_element))

    return wrapper


def single_subclass_aggr(func: Callable[[Any, Element], R]) -> Callable[[Any, Element], R]:
    @wraps(func)
    def wrapper(self: BetterParser, xml_element: Element) -> R:
        children = tuple(xml_element)
        if len(children) != 1:
            raise ValueError
        return func(self, children[0])

    return wrapper


def ref_variation(
        direct_func: Callable | None = None,
        /, *,
        element_name: str | None = None,
):
    """
    Applies the function to all children of the XML element.
    Automatically checks and report children with unexpected tag.
    :param direct_func: Function to be wrapped, if expected_name not provided (default will be used).
    :param element_name: Expected child element tag, if different from default.
    :return: Filtered (not None) list of processed elements.
    """
    def decorator(
            func: Callable[[Any, Element], str | None],
    ) -> Callable[[Any, Element], list[str] | None]:
        @wraps(func)
        def wrapper(self: BetterParser, xml_element: Element | None) -> list[str] | None:
            def apply_handler(child: Element) -> str | None:
                if child.tag != f'{element_name}-REF-CONDITIONAL':
                    if child.tag not in invalid_tags:
                        self._logger.warning(f'Unexpected item {child.tag} in collection {xml_element.tag}')
                        invalid_tags.add(child.tag)
                    return None
                if (ref := child.find(f'{element_name}-REF')) is None:
                    self._logger.warning(f'Missing ref element for {child.tag} in collection {xml_element.tag}')
                    return None
                return func(self, ref)

            nonlocal element_name
            if xml_element is None:
                return None
            invalid_tags = set()
            if element_name is None:
                element_name = xml_element.tag.removesuffix('S')
            return list(filter(not_none, map(apply_handler, xml_element)))

        return wrapper

    if direct_func is not None:
        return decorator(direct_func)
    return decorator


def eval_children(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return ArObject.eval_children(func(*args, **kwargs))

    return wrapper


class BetterParser(BaseParser, ABC):
    _handlers: dict[str, HandlerMethod]

    def __init__(self, *args, **kwargs):
        if not hasattr(self.__class__, '_handlers'):
            self.__class__._collect_handlers()
        super().__init__(*args, **kwargs)
        self._missing_required = {
            h.specs.tag
            for h in self._handlers.values()
            if h.specs.required
        }
        self._unexpected = set()
        self._not_implemented = set()
        self._invalid = set()

    @staticmethod
    def _tag_list(tags: set[str]) -> str:
        return ', '.join(tags)

    @classmethod
    def _collect_handlers(cls):
        cls._handlers = dict(chain.from_iterable(
            ((t, m) for t in m.specs.all_supported_tags)
            for n in dir(cls)
            if isinstance(m := getattr(cls, n), HandlerMethod)
        ))

    def _get_handler(self, tag_name: str) -> HandlerMethod | None:
        try:
            return self._handlers[tag_name]
        except KeyError:
            return None

    def _handle(self, xml_element: Element) -> tuple[str, Any] | None:
        element_handler = self._get_handler(xml_element.tag)
        if element_handler is None:
            self._handle_unknown(xml_element)
            return None
        if element_handler.specs.param is None:
            self._not_implemented.add(xml_element.tag)
            return None
        try:
            result = element_handler(self, xml_element)
        except ValueError:
            self._invalid.add(xml_element.tag)
            return None
        except NotImplementedError:
            self._not_implemented.add(xml_element.tag)
            return None
        except NameError:
            self._handle_unknown(xml_element)
            return None
        if result is Skip:
            return None
        if element_handler.specs.required:
            self._missing_required.remove(xml_element.tag)
        return element_handler.specs.param, result

    def _handle_unknown(self, xml_element: Element) -> None:
        self._unexpected.add(xml_element.tag)

    def _parse_attributes(self, xml_element: Element) -> dict[str, Any]:
        if len(xml_element.attrib) > 0:
            self._logger.warning(f'Unhandled XML attributes in element {xml_element.tag}')
        return {}

    def _scan_element(self, xml_element: Element) -> dict[str, Any] | None:
        element_kwargs = dict(filter(not_none, map(self._handle, xml_element)))
        attribute_kwargs = self._parse_attributes(xml_element)
        if len(self._missing_required) > 0:
            self._logger.error(f'Element {xml_element.tag} will be ignored, missing required tags: {self._tag_list(self._missing_required)}')
            return None
        if len(self._invalid) > 0:
            self._logger.error(f'Element {xml_element.tag} will be ignored, invalid values in tags: {self._tag_list(self._invalid)}')
            return None
        if len(self._unexpected) > 0:
            self._logger.warning(f'Unexpected tags in {xml_element.tag}: {self._tag_list(self._unexpected)}')
        if len(self._not_implemented) > 0:
            self._logger.warning(f'Element {xml_element.tag}: Parser not implemented for tags {self._tag_list(self._not_implemented)}')
        return element_kwargs | attribute_kwargs

    @abstractmethod
    def parse_element(self, xml_element: Element | None, parent: MaybeArObject = None) -> Any:
        raise NotImplementedError


C = TypeVar('C', bound=ArObject)
V = TypeVar('V', bound=ArObject)


class ParserSelector(BetterParser, Generic[C]):
    """
    Selects and runs parser for the given tag.
    Raises on init:
        - NotImplementedError if a not implemented tag is encountered
        - NameError if an unexpected tag (neither implemented nor not) is encountered
    """
    _not_implemented: set[str] = set()
    _tag_map: dict[str, type[BetterParser]]

    def __init__(
            self,
            tag_name: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        try:
            self._parser: BetterParser = self._tag_map[tag_name]()
        except KeyError:
            if tag_name in self._not_implemented:
                raise NotImplementedError
            raise NameError

    def parse_element(self, xml_element: Element | None, parent: MaybeArObject = None) -> C | None:
        return self._parser.parse_element(xml_element, parent)


class BasicParser(BetterParser, Generic[C]):
    _returned_type: type[C]

    def parse_element(self, xml_element: Element | None, parent: MaybeArObject = None) -> C | None:
        if xml_element is None:
            return None
        kwargs = self._scan_element(xml_element)
        if kwargs is None:
            return None
        return self._returned_type(**kwargs)


class PropertySetParser(BasicParser[C], Generic[C, V]):
    _variant_parser_type: type[BasicParser[V]]
    _tag: str

    @classmethod
    def _collect_handlers(cls):
        cls._parse_variants.specs = HandlerSpecs(
            tag=f'{cls._tag}-VARIANTS',
            param='variants',
        )
        super()._collect_handlers()

    @multiple
    def _parse_variants(self, xml_element: Element) -> V | None:
        if xml_element.tag != f'{self._tag}-CONDITIONAL':
            raise NameError
        parser = self._variant_parser_type()
        return parser.parse_element(xml_element)
