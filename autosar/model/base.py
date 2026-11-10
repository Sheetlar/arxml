import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable, TYPE_CHECKING, Any
from xml.etree.ElementTree import Element

from autosar.model.admin_data import AdminData
from autosar.model.ar_object import ArObject, ArObjectWithParent
from autosar.model.atp_variation import Variants
from autosar.model.enums import IntervalTypeEnum, DataFilterTypeEnum
from autosar.model.languages_enum import LEnum

if TYPE_CHECKING:
    from autosar.model.element import Element as ArElement

p_version = re.compile(r"(\d+)\.(\d+)\.(\d+)")


class Limit:
    interval_type: str = IntervalTypeEnum.CLOSED


class FloatLimit(float, Limit):
    pass


class IntLimit(int, Limit):
    pass


class LangStr(str):
    language: LEnum | None = None


@dataclass
class ShortNameFragment(ArObject):
    fragment: str
    role: str


class Referrable(ArObjectWithParent):
    def __init__(
            self,
            name: str,
            short_name_fragments: Iterable[ShortNameFragment] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.short_name_fragments = self.eval_children(short_name_fragments)

    @property
    def ref(self) -> str:
        return f'{self.parent.namespace}/{self.name}'

    @property
    def namespace(self) -> str:
        return self.ref

    def _repr_params_str(self, params: dict[str, Any]) -> str:
        name = params.pop('name', None)
        params_str = super()._repr_params_str(params)
        return f'{name=}, {params_str}'


class Identifiable(Referrable):
    _valid_categories: type[StrEnum]

    def __init__(
            self,
            admin_data: AdminData | None = None,
            category: str | None = None,
            desc: LangStr | None = None,
            long_name: LangStr | None = None,
            uuid: str | None = None,
            annotation: None = None,
            introduction: None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.admin_data = admin_data
        self.category = category
        self.desc = desc
        self.long_name = long_name
        self.uuid = uuid
        self.annotation = annotation
        self.introduction = introduction
        self._validate_category()

    def _validate_category(self):
        if not hasattr(self, '_valid_categories'):
            return
        if self.category is None:
            self._logger.warning(f'Category of {self.__class__.__name__} "{self.name}" is not set')
            return
        try:
            self.category = self._valid_categories(self.category)
        except ValueError:
            self._logger.warning(f'Category of {self.__class__.__name__} "{self.name}" is not valid: {self.category}')


class Describable(ArObject):
    _valid_categories: type[StrEnum]

    def __init__(
            self,
            admin_data: AdminData | None = None,
            category: str | None = None,
            desc: LangStr | None = None,
            introduction: None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.admin_data = admin_data
        self.category = category
        self.desc = desc
        self.introduction = introduction
        self._validate_category()

    def _validate_category(self):
        if not hasattr(self, '_valid_categories'):
            return
        if self.category is None:
            self._logger.warning(f'Category of {self.__class__.__name__} "{self.name}" is not set')
            return
        try:
            self.category = self._valid_categories(self.category)
        except ValueError:
            self._logger.warning(f'Category of {self.__class__.__name__} "{self.name}" is not valid: {self.category}')


class OldAdminData(ArObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.special_data_groups: list[SpecialDataGroup] = []

    def asdict(self):
        return {
            'type': self.__class__.__name__,
            'specialDataGroups': [elem.asdict() for elem in self.special_data_groups],
        }

    def __eq__(self, other):
        if isinstance(other, self.__class__) and len(self.special_data_groups) == len(other.special_data_groups):
            for i, elem in enumerate(self.special_data_groups):
                if elem != other.special_data_groups[i]:
                    return False
            return True
        return False

    def __ne__(self, other):
        return not (self == other)

    def find(self, ref: str):
        name, _, tail = ref.partition('/')
        for sdg in self.special_data_groups:
            if sdg.sdg_gid == name:
                if len(tail) > 0:
                    return sdg.find(tail)
                return sdg
        return None


class SpecialDataGroup(ArObject):
    def __init__(self, sdg_gid: str, sd: str | None = None, sd_gid: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sdg_gid = sdg_gid
        self.sdg: list[SpecialDataGroup] = []
        self.sd: list[SpecialData] = []
        if sd is not None or sd_gid is not None:
            self.sd.append(SpecialData(sd, sd_gid))

    def asdict(self):
        data = {'type': self.__class__.__name__}
        if self.sdg_gid is not None:
            data['SDG_GID'] = self.sdg_gid
        if self.sd is not None:
            data['SD'] = self.sd
        # if self.SD_GID is not None:
        #     data['SD_GID'] = self.SD_GID
        return data

    def find(self, ref: str):
        name, _, tail = ref.partition('/')
        for sd in self.sd:
            if sd.gid == name:
                return sd
        for sdg in self.sdg:
            if sdg.sdg_gid == name:
                if len(tail) > 0:
                    return sdg.find(tail)
                return sdg
        return None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.sdg_gid == other.sdg_gid:
                for i, sd in enumerate(self.sd):
                    other_sd = other.sd[i]
                    if sd.text != other_sd.text or sd.gid != other_sd.gid:
                        return False
                return True
        return False

    def __ne__(self, other):
        return not (self == other)


class SpecialData(ArObject):
    def __init__(self, text: str, gid: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self.gid = gid


def split_ref(ref: str):
    """splits an autosar url string into an array"""
    if isinstance(ref, str):
        if ref[0] == '/':
            return ref[1:].split('/')
        else:
            return ref.split('/')
    return None


def has_admin_data(xml_root: Element):
    return xml_root.find('ADMIN-DATA') is not None


def parse_admin_data_node(xml_root: Element):
    if xml_root is None:
        return None
    assert (xml_root.tag == 'ADMIN-DATA')
    admin_data = OldAdminData()
    xml_sdgs = xml_root.find('./SDGS')
    if xml_sdgs is not None:
        for xmlElem in xml_sdgs.findall('./SDG'):
            gid = xmlElem.attrib['GID']
            sd = None
            sd_gid = None
            xml_sd = xmlElem.find('SD')
            if xml_sd is not None:
                sd = xml_sd.text
                if 'GID' in xml_sd.attrib:
                    sd_gid = xml_sd.attrib['GID']
            admin_data.special_data_groups.append(SpecialDataGroup(gid, sd, sd_gid))
    return admin_data


def parse_text_node(xml_elem: Element):
    return xml_elem.text if xml_elem is not None else None


def create_admin_data(data: dict[str, Any]):
    admin_data = OldAdminData()
    sdg_gid: str | None = data.get('SDG_GID', None)
    if 'SDG' in data:
        group = SpecialDataGroup(sdg_gid)
        for item in data['SDG']:
            sd_gid = item.get('SD_GID', None)
            sd = item.get('SD', None)
            group.sd.append(SpecialData(sd, sd_gid))
        admin_data.special_data_groups.append(group)
    else:
        sd_gid = data.get('SD_GID', None)
        sd = data.get('SD', None)
        admin_data.special_data_groups.append(SpecialDataGroup(sdg_gid, sd, sd_gid))
    return admin_data


def parse_autosar_version_and_schema(xml_root: Element):
    """
    Parses AUTOSAR version from the schemaLocation attribute in the root AUTOSAR tag

    For AUTOSAR versions 4.3 and below (e.g. "http://autosar.org/schema/r4.0 AUTOSAR_4-3-0.xsd")
    Returns a tuple with major, minor, patch, None, schemaFile. Types are (int, int, int, NoneType, str)

    For AUTOSAR versions 4.4 and above (e.g. "http://autosar.org/schema/r4.0 AUTOSAR_00044.xsd")
    Returns a tuple with major, minor, None, release, schemaFile
    This will now report (major,minor) as (4,0) since it will now extract from the "r4.0"-part of the attribute.
    """
    for key in xml_root.attrib.keys():
        if key.endswith('schemaLocation'):
            value = xml_root.attrib[key]
            # Retrieve the schema file
            tmp = value.partition(' ')
            if len(tmp[2]) > 0:
                schema_file = tmp[2]
            else:
                schema_file = None
            # Is this AUTOSAR 3?
            result = re.search(r'(\d)\.(\d)\.(\d)', value)
            if result is not None:
                return int(result.group(1)), int(result.group(2)), int(result.group(3)), None, schema_file
            else:
                # Is this AUTOSAR 4.0 to 4.3?
                result = re.search(r'(\d)-(\d)-(\d).*\.xsd', value)
                if result is not None:
                    return int(result.group(1)), int(result.group(2)), int(result.group(3)), None, schema_file
                else:
                    # Is this AUTOSAR 4.4 or above?
                    result = re.search(r'r(\d+)\.(\d+)\s+AUTOSAR_(\d+).xsd', value)
                    if result is not None:
                        return int(result.group(1)), int(result.group(2)), None, int(result.group(3)), schema_file

    return None, None, None, None, None


def parse_version_string(version_string: str):
    """
    takes a string of the format <major>.<minor>.<patch> (e.g. "3.2.2") and returns a tuple with three integers (major, minor, patch)
    """
    result = p_version.match(version_string)
    if result is None:
        raise ValueError("VersionString argument did not match the pattern '<major>.<minor>.<patch>'")
    else:
        return int(result.group(1)), int(result.group(2)), int(result.group(3))


def find_unique_name_in_list(element_list: list['ArElement'], base_name: str):
    """
    Attempts to find a unique name in the list of objects based on baseName.
    This function can modify names in gived list.
    Returns a new name which is guaranteed to be unique
    """

    found_elem = None
    highest_index = 0
    has_index = False
    p0 = re.compile(base_name + r'_(\d+)')
    for elem in element_list:
        result = p0.match(elem.name)
        if result is not None:
            has_index = True
            index = int(result.group(1))
            if index > highest_index:
                highest_index = index
        elif elem.name == base_name:
            found_elem = elem
    if found_elem is not None:
        found_elem.name = '_'.join([found_elem.name, '0'])
    if has_index or found_elem is not None:
        return '_'.join([base_name, str(highest_index + 1)])
    else:
        return base_name


class SwDataDefProps(ArObject):
    @staticmethod
    def tag(*_):
        return 'SW-DATA-DEF-PROPS-CONDITIONAL'

    def __init__(
            self,
            base_type_ref: str | None = None,
            implementation_type_ref: str | None = None,
            sw_address_method_ref: str | None = None,
            sw_calibration_access: str | None = None,
            sw_impl_policy: str | None = None,
            sw_pointer_target_props: 'SwPointerTargetProps | None' = None,
            sw_record_layout_ref: str | None = None,
            compu_method_ref: str | None = None,
            data_constraint_ref: str | None = None,
            unit_ref: str | None = None,
            parent: ArObject | None = None,
            *args, **kwargs,  # TODO: More params
    ):
        super().__init__(*args, **kwargs)
        self.base_type_ref = base_type_ref
        self.sw_calibration_access = sw_calibration_access
        self.sw_address_method_ref = sw_address_method_ref
        self.sw_record_layout_ref = sw_record_layout_ref
        self.compu_method_ref = compu_method_ref
        self.data_constraint_ref = data_constraint_ref
        self.implementation_type_ref = implementation_type_ref
        self.sw_pointer_target_props = sw_pointer_target_props
        self.unit_ref = unit_ref
        self._sw_impl_policy = sw_impl_policy
        self.parent = parent

    @property
    def sw_impl_policy(self):
        return self._sw_impl_policy

    @sw_impl_policy.setter
    def sw_impl_policy(self, value: str):
        if value is None:
            self._sw_impl_policy = None
        else:
            uc_value = value.upper()
            enum_values = ["CONST", "FIXED", "MEASUREMENT-POINT", "QUEUED", "STANDARD"]
            if uc_value in enum_values:
                self._sw_impl_policy = uc_value
            else:
                raise ValueError(f'invalid swImplPolicy value: {value}')

    def has_any_prop(self):
        """
        Returns True if any internal attribute is not None, else False.
        The check excludes the parent attribute.
        """
        retval = False
        attr_names = [
            'base_type_ref',
            'sw_calibration_access',
            'sw_address_method_ref',
            'compu_method_ref',
            'data_constraint_ref',
            'implementation_type_ref',
            'sw_pointer_target_props',
            'unit_ref',
            'sw_impl_policy'
        ]
        for name in attr_names:
            if getattr(self, name) is not None:
                retval = True
                break
        return retval


class SwDataDefPropsVariants(Variants[SwDataDefProps]):
    pass


class SwPointerTargetProps:
    """
    (AUTOSAR 4)
    Implements <SW-POINTER-TARGET-PROPS>
    """

    @staticmethod
    def tag(*_):
        return 'SW-POINTER-TARGET-PROPS'

    def __init__(self, target_category: str | None = None, variants: SwDataDefProps | Iterable | None = None):
        self.target_category = target_category
        if variants is None:
            self.variants = []
        elif isinstance(variants, SwDataDefProps):
            self.variants = [variants]
        else:
            self.variants = list(variants)


class SymbolProps:
    """
    (AUTOSAR 4)
    Implements <SYMBOL-PROPS>
    """

    @staticmethod
    def tag(*_):
        return 'SYMBOL-PROPS'

    def __init__(self, name: str | None = None, symbol: str | None = None):
        self.name = name
        self.symbol = symbol


@dataclass
class DataFilter(ArObject):
    data_filter_type: DataFilterTypeEnum | None = None
    mask: int | None = None
    max: int | None = None
    min: int | None = None
    offset: int | None = None
    period: int | None = None
    x: int | None = None


# Exceptions
class InvalidUnitRef(ValueError):
    pass


class InvalidPortInterfaceRef(ValueError):
    pass


class InvalidComponentTypeRef(ValueError):
    pass


class InvalidDataTypeRef(ValueError):
    pass


class InvalidDataElementRef(ValueError):
    pass


class InvalidPortRef(ValueError):
    pass


class InvalidInitValueRef(ValueError):
    pass


class InvalidDataConstraintRef(ValueError):
    pass


class InvalidCompuMethodRef(ValueError):
    pass


class DataConstraintError(ValueError):
    pass


class InvalidMappingRef(ValueError):
    pass


class InvalidModeGroupRef(ValueError):
    pass


class InvalidModeDeclarationGroupRef(ValueError):
    pass


class InvalidModeDeclarationRef(ValueError):
    pass


class InvalidEventSourceRef(ValueError):
    pass


class InvalidRunnableRef(ValueError):
    pass


class InvalidBehaviorRef(ValueError):
    pass


class InvalidSwAddrMethodRef(ValueError):
    pass
