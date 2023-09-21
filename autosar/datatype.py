import copy
from typing import Iterable

from autosar.ar_object import ArObject
from autosar.base import AdminData, DataConstraintError, SwDataDefPropsConditional, SwPointerTargetProps, SymbolProps, InvalidDataTypeRef
from autosar.element import Element


class RecordTypeElement(Element):
    """
    (AUTOSAR3)
    Implementation of <RECORD-ELEMENT> (found inside <RECORD-TYPE>).

    """

    @staticmethod
    def tag(*_):
        return 'RECORD-ELEMENT'

    def __init__(self, name: str, type_ref: str, parent: ArObject | None = None, admin_data: AdminData | None = None):
        super().__init__(name, parent, admin_data)
        self.type_ref = type_ref

    def __eq__(self, other):
        if self is other:
            return True
        if type(self) == type(other):
            if self.name == other.name:
                lhs = None if self.type_ref is None else self.root_ws().find(self.type_ref)
                rhs = None if other.type_ref is None else other.root_ws().find(other.type_ref)
                if lhs != rhs:
                    print(self.name, self.type_ref)
                return lhs == rhs
        return False


class CompuScaleElement:
    """
    Implementation of <COMPU-SCALE>
    """

    @staticmethod
    def tag(*_):
        return 'COMPU-SCALE'

    def __init__(
            self,
            lower_limit: int | float,
            upper_limit: int | float,
            lower_limit_type: str = 'CLOSED',
            upper_limit_type: str = 'CLOSED',
            label: str | None = None,
            symbol: str | None = None,
            text_value: str | None = None,
            numerator: int | float | None = None,
            denominator: int | None = None,
            offset: int | float | None = None,
            mask: int | None = None,
            admin_data: AdminData | None = None,
    ):
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.lower_limit_type = lower_limit_type
        self.upper_limit_type = upper_limit_type
        self.symbol = symbol
        self.label = label
        self.admin_data = admin_data
        self.text_value = text_value
        self.offset = offset
        self.numerator = numerator
        self.denominator = denominator
        self.mask = mask


class Unit(Element):
    """
    Implementation of <UNIT>
    """

    @staticmethod
    def tag(*_):
        return 'UNIT'

    def __init__(
            self,
            name: str,
            display_name: str,
            factor: int | float | None = None,
            offset: int | float | None = None,
            parent: ArObject | None = None,
    ):
        super().__init__(name, parent)
        self.display_name = display_name
        self.factor = factor  # only supported in AUTOSAR 4 and above
        self.offset = offset  # only supported in AUTOSAR 4 and above

    def __eq__(self, other):
        if self is other:
            return True
        if type(self) is type(other):
            if (self.name == other.name) and (self.display_name == other.display_name) and (
                    self.factor == other.factor) and (self.offset == other.offset):
                return True
        return False


class DataType(Element):
    """
    Base type for DataType (AUTOSAR3)
    """

    def __init__(self, name: str, parent: ArObject | None = None, admin_data: AdminData | None = None):
        super().__init__(name, parent, admin_data)

    @property
    def is_complex_type(self):
        return True if isinstance(self, (RecordDataType, ArrayDataType)) else False


class IntegerDataType(DataType):
    """
    IntegerDataType (AUTOSAR3)
    """

    @staticmethod
    def tag(*_):
        return 'INTEGER-TYPE'

    def __init__(
            self,
            name: str,
            min_val: int = 0,
            max_val: int = 0,
            compu_method_ref: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.min_val = int(min_val)
        self.max_val = int(max_val)
        self._min_value_type = 'CLOSED'
        self._max_value_type = 'CLOSED'

        if isinstance(compu_method_ref, str):
            self.compu_method_ref = compu_method_ref
        elif hasattr(compu_method_ref, 'ref'):
            self.compu_method_ref = compu_method_ref.ref
        else:
            self.compu_method_ref = None

    @property
    def min_value_type(self):
        return self._min_value_type

    @min_value_type.setter
    def min_value_type(self, value: str):
        if (value != "CLOSED") and (value != "OPEN"):
            raise ValueError('Value must be either "CLOSED" or "OPEN"')
        self._min_value_type = value

    @property
    def max_value_type(self):
        return self._max_value_type

    @max_value_type.setter
    def max_value_type(self, value: str):
        if (value != "CLOSED") and (value != "OPEN"):
            raise ValueError('Value must be either "CLOSED" or "OPEN"')
        self._min_value_type = value

    def __eq__(self, other):
        if self is other:
            return True
        if type(other) is type(self):
            if (self.name == other.name) and (self.min_val == other.min_val) and (self.max_val == other.max_val):
                if (self.compu_method_ref is not None) and (other.compu_method_ref is not None):
                    return self.root_ws().find(self.compu_method_ref) == other.root_ws().find(other.compu_method_ref)
                elif (self.compu_method_ref is None) and (other.compu_method_ref is None):
                    return True

    def __deepcopy__(self, memo):
        obj = type(self)(self.name, self.min_val, self.max_val, self.compu_method_ref)
        if self.admin_data is not None:
            obj.admin_data = copy.deepcopy(self.admin_data, memo)
        return obj


class RecordDataType(DataType):
    """
    RecordDataType (AUTOSAR3)
    """

    @staticmethod
    def tag(*_):
        return 'RECORD-TYPE'

    def __init__(
            self,
            name: str,
            elements: Iterable[RecordTypeElement] | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.elements = []
        if elements is not None:
            for elem in elements:
                if isinstance(elem, RecordTypeElement):
                    self.elements.append(elem)
                    elem.parent = self
                else:
                    raise ValueError('Element must be an instance of RecordTypeElement')

    def __eq__(self, other):
        if self is other:
            return True
        if (self.name == other.name) and (len(self.elements) == len(other.elements)):
            for i in range(len(self.elements)):
                if self.elements[i] != other.elements[i]:
                    return False
            return True
        return False

    def __deepcopy__(self, memo):
        obj = type(self)(self.name)
        if self.admin_data is not None:
            obj.admin_data = copy.deepcopy(self.admin_data, memo)
        for elem in self.elements:
            obj.elements.append(RecordTypeElement(elem.name, elem.type_ref, self))
        return obj


class ArrayDataType(DataType):
    """
    ArrayDataType (AUTOSAR 3)
    """

    @staticmethod
    def tag(*_):
        return 'ARRAY-TYPE'

    def __init__(
            self,
            name: str,
            type_ref: str,
            length: int,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.type_ref = type_ref
        self.length = length


class BooleanDataType(DataType):
    """
    BooleanDataType (AUTOSAR 3)
    """

    @staticmethod
    def tag(*_):
        return 'BOOLEAN-TYPE'

    def __init__(self, name: str, parent: ArObject | None = None, admin_data: AdminData | None = None):
        super().__init__(name, parent, admin_data)


class StringDataType(DataType):
    """
    StringDataType (AUTOSAR 3)
    """

    @staticmethod
    def tag(*_):
        return 'STRING-TYPE'

    def __init__(
            self,
            name: str,
            length: int,
            encoding: str,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.length = length
        self.encoding = encoding

    def asdict(self):
        data = {
            'type': self.__class__.__name__,
            'name': self.name,
            'encoding': self.encoding,
            'length': self.length,
        }
        return data

    def __eq__(self, other):
        if self is other:
            return False
        if type(self) == type(other):
            if (self.name == other.name) and (self.length == other.length) and (self.encoding == other.encoding):
                return True
        return False

    def __deepcopy__(self, memo):
        obj = type(self)(self.name, self.length, self.encoding)
        return obj


class RealDataType(DataType):
    """
    RealDataType (AUTOSAR 3)
    """

    @staticmethod
    def tag(*_):
        return 'REAL-TYPE'

    def __init__(
            self,
            name: str,
            min_val: int | float | str | None,
            max_val: int | float | str | None,
            min_val_type: str = 'CLOSED',
            max_val_type: str = 'CLOSED',
            has_nan: bool = False,
            encoding: str = 'SINGLE',
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.min_val = min_val
        self.max_val = max_val
        self.min_val_type = min_val_type
        self.max_val_type = max_val_type
        self.has_nan = has_nan
        self.encoding = encoding


class Computation:
    """
    Represents one computation (COMPU-INTERNAL-TO-PHYS or COMPU-PHYS-TO-INTERNAL).
    Contains a list of CompuScaleElement objects as well as an optional defaultValue.
    """

    def __init__(self, default_value: int | float | str | None = None):
        self.elements: list[CompuScaleElement] = []  # list of CompuScaleElement
        self.default_value = default_value

    @property
    def lower_limit(self):
        """
        Returns lowerLimit of first element
        """
        if len(self.elements) > 0:
            return self.elements[0].lower_limit
        else:
            raise KeyError('No elements in Computation object')

    @property
    def upper_limit(self):
        """
        Returns upperLimit of last element
        """
        if len(self.elements) > 0:
            return self.elements[-1].upper_limit
        else:
            raise KeyError('No elements in Computation object')

    def create_value_table(self, elements: Iterable[str | tuple], auto_label: bool = True):
        """
        Creates a list of CompuScaleElements based on contents of the elements argument

        When elements is a list of strings:
            Creates one CompuScaleElement per list item and automatically calculates lower and upper limits

        When elements is a list of tuples:
            If 2-tuple: First element is both lower_limit and upper_limit, second element is text_value.
            If 3-tuple: First element is lower_limit, second element is upper_limit, third element is text_value.

        autoLabel: automatically creates a <SHORT-LABEL> based on the element.text_value (bool). Default=True
        """
        lower_limit_type, upper_limit_type = 'CLOSED', 'CLOSED'
        for elem in elements:
            if isinstance(elem, str):
                limit = len(self.elements)
                (lower_limit, upper_limit, text_value) = (limit, limit, elem)
            elif isinstance(elem, tuple):
                if len(elem) == 2:
                    (limit, text_value) = elem
                    (lower_limit, upper_limit, text_value) = (limit, limit, text_value)
                elif len(elem) == 3:
                    lower_limit, upper_limit, text_value = elem
                else:
                    raise ValueError(f'Invalid length: {len(elem)}')
            else:
                raise ValueError(f'Type not supported: {type(elem)}')
            label = text_value if auto_label else None
            self.elements.append(CompuScaleElement(
                lower_limit,
                upper_limit,
                lower_limit_type,
                upper_limit_type,
                text_value=text_value,
                label=label,
            ))

    def create_rational_scaling(
            self,
            offset: int | float | None,
            numerator: int | float | None,
            denominator: int | None,
            lower_limit: int | float,
            upper_limit: int | float,
            lower_limit_type: str = 'CLOSED',
            upper_limit_type: str = 'CLOSED',
            label: str | None = None,
            symbol: str | None = None,
            admin_data=None,
    ):
        """
        Creates COMPU-SCALE based on rational scaling
        """
        element = CompuScaleElement(
            lower_limit,
            upper_limit,
            lower_limit_type,
            upper_limit_type,
            label=label,
            symbol=symbol,
            offset=offset,
            numerator=numerator,
            denominator=denominator,
            admin_data=admin_data,
        )
        self.elements.append(element)
        return element

    def create_bit_mask(self, elements: Iterable[tuple], auto_label: bool = True):
        """
        When elements is a list of tuples:

            If 2-tuple: First element is the bitmask (int), second element is the symbol (str)
        """
        lower_limit_type, upper_limit_type = 'CLOSED', 'CLOSED'
        for elem in elements:
            if isinstance(elem, tuple):
                if len(elem) == 2:
                    (mask, symbol) = elem
                    (lower_limit, upper_limit) = (mask, mask)
                else:
                    raise ValueError(f'Invalid length: {len(elem)}')
            else:
                raise ValueError(f'Type not supported: {type(elem)}')
            label = symbol if auto_label else None
            self.elements.append(CompuScaleElement(
                lower_limit,
                upper_limit,
                lower_limit_type,
                upper_limit_type,
                symbol=symbol,
                label=label,
                mask=mask,
            ))


class CompuMethod(Element):
    """
    CompuMethod class
    """

    @staticmethod
    def tag(*_):
        return 'COMPU-METHOD'

    def __init__(
            self,
            name: str,
            use_int_to_phys: bool,
            use_phys_to_int: bool,
            unit_ref: str | None = None,
            category: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data, category)
        self.unit_ref = unit_ref
        self.int_to_phys = None
        self.phys_to_int = None
        if use_int_to_phys:
            self.int_to_phys = Computation()
        if use_phys_to_int:
            self.phys_to_int = Computation()


class ConstraintBase:
    def __init__(
            self,
            lower_limit: int | float | str | None,
            upper_limit: int | float | str | None,
            lower_limit_type: str,
            upper_limit_type: str,
    ):
        if lower_limit is not None:
            if isinstance(lower_limit, str) and lower_limit != '-INF':
                raise ValueError(f'Unknown lowerLimit: {lower_limit}')
            self.lower_limit = lower_limit
        if upper_limit is not None:
            if isinstance(upper_limit, str) and upper_limit != 'INF':
                raise ValueError(f'Unknown upperLimit: {upper_limit}')
            self.upper_limit = upper_limit
        if lower_limit_type == 'CLOSED' or lower_limit_type == 'OPEN':
            self.lower_limit_type = lower_limit_type
        else:
            raise ValueError(lower_limit_type)
        if upper_limit_type == 'CLOSED' or upper_limit_type == 'OPEN':
            self.upper_limit_type = upper_limit_type
        else:
            raise ValueError(upper_limit_type)

    def check_value(self, value: int | float):
        if ((self.lower_limit_type == 'CLOSED') and (value < self.lower_limit)) or ((self.lower_limit_type == 'OPEN') and (value <= self.lower_limit)):
            raise DataConstraintError(f'Value {value} outside lower data constraint ({self.lower_limit}) ')
        if ((self.upper_limit_type == 'CLOSED') and (value > self.upper_limit)) or ((self.upper_limit_type == 'OPEN') and (value >= self.upper_limit)):
            raise DataConstraintError(f'Value {value} outside upper data constraint ({self.upper_limit}) ')


class InternalConstraint(ConstraintBase):
    def __init__(
            self,
            lower_limit: int | float | str | None = None,
            upper_limit: int | float | str | None = None,
            lower_limit_type: str = 'CLOSED',
            upper_limit_type: str = 'CLOSED',
    ):
        super().__init__(lower_limit, upper_limit, lower_limit_type, upper_limit_type)


class PhysicalConstraint(ConstraintBase):
    def __init__(
            self,
            lower_limit: int | float | str | None = None,
            upper_limit: int | float | str | None = None,
            lower_limit_type: str = 'CLOSED',
            upper_limit_type: str = 'CLOSED',
    ):
        super().__init__(lower_limit, upper_limit, lower_limit_type, upper_limit_type)


class DataConstraint(Element):
    @staticmethod
    def tag(*_):
        return 'DATA-CONSTR'

    def __init__(
            self,
            name,
            rules: Iterable[dict[str, int | float | str]],
            constraint_level: int | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.level = constraint_level
        self.rules: list[InternalConstraint | PhysicalConstraint] = []
        for rule in rules:
            if rule['type'] == 'internalConstraint':
                self.rules.append(InternalConstraint(
                    lower_limit=rule['lowerLimit'],
                    upper_limit=rule['upperLimit'],
                    lower_limit_type=rule['lowerLimitType'],
                    upper_limit_type=rule['upperLimitType'],
                ))
            elif rule['type'] == 'physicalConstraint':
                self.rules.append(PhysicalConstraint(
                    lower_limit=rule['lowerLimit'],
                    upper_limit=rule['upperLimit'],
                    lower_limit_type=rule['lowerLimitType'],
                    upper_limit_type=rule['upperLimitType'],
                ))
            else:
                raise NotImplementedError

    @property
    def constraint_level(self):
        if self.level is None or isinstance(self.level, int):
            return self.level
        else:
            raise ValueError(f'Unknown constraintLevel: {self.level}')

    @property
    def lower_limit(self):
        if len(self.rules) == 1:
            return self.rules[0].lower_limit
        else:
            raise NotImplementedError('Only a single constraint rule supported')

    @property
    def upper_limit(self):
        if len(self.rules) == 1:
            return self.rules[0].upper_limit
        else:
            raise NotImplementedError('Only a single constraint rule supported')

    @property
    def lower_limit_type(self):
        if len(self.rules) == 1:
            return self.rules[0].lower_limit_type
        else:
            raise NotImplementedError('Only a single constraint rule supported')

    @property
    def upper_limit_type(self):
        if len(self.rules) == 1:
            return self.rules[0].upper_limit_type
        else:
            raise NotImplementedError('Only a single constraint rule supported')

    def check_value(self, v: int | float):
        if len(self.rules) == 1:
            self.rules[0].check_value(v)
        else:
            raise NotImplementedError('Only a single rule constraint supported')

    def find_by_type(self, constraint_type: str = 'internalConstraint'):
        """
        Returns the first constraint of the given constraint type (internalConstraint or physicalConstraint)
        """
        for rule in self.rules:
            if (isinstance(rule, InternalConstraint) and constraint_type == 'internalConstraint') or (
                    isinstance(rule, PhysicalConstraint) and constraint_type == 'physicalConstraint'):
                return rule


class ImplementationDataTypeBase:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variant_props: list[SwDataDefPropsConditional | SwPointerTargetProps] = []

    def get_type_reference(self):
        """
        Deprecated, use implementationTypeRef property instead
        """
        return self.implementation_type_ref

    @property
    def base_type_ref(self):
        if len(self.variant_props) > 0:
            return self.variant_props[0].base_type_ref
        return None

    @property
    def data_constraint_ref(self):
        if len(self.variant_props) > 0:
            return self.variant_props[0].data_constraint_ref
        return None

    @property
    def implementation_type_ref(self):
        if len(self.variant_props) > 0:
            return self.variant_props[0].implementation_type_ref
        return None

    @property
    def compu_method_ref(self):
        if len(self.variant_props) > 0:
            return self.variant_props[0].compu_method_ref
        return None


class ImplementationDataType(Element, ImplementationDataTypeBase):
    @staticmethod
    def tag(*_):
        return 'IMPLEMENTATION-DATA-TYPE'

    def __init__(
            self,
            name: str,
            variant_props: SwDataDefPropsConditional | SwPointerTargetProps | Iterable[SwDataDefPropsConditional | SwPointerTargetProps] | None = None,
            dynamic_array_size_profile: str | None = None,
            type_emitter: str | None = None,
            category: str = 'VALUE',
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data, category)
        self.dynamic_array_size_profile = dynamic_array_size_profile
        self.type_emitter = type_emitter
        self.sub_elements: list[ImplementationDataTypeElement] = []
        self.symbol_props: SymbolProps | None = None
        if isinstance(variant_props, (SwDataDefPropsConditional, SwPointerTargetProps)):
            self.variant_props.append(variant_props)
        elif isinstance(variant_props, Iterable):
            for elem in variant_props:
                if isinstance(elem, (SwDataDefPropsConditional, SwPointerTargetProps)):
                    self.variant_props.append(elem)
                else:
                    raise ValueError('Invalid type: ', type(elem))
        if self.category == 'TYPE_REFERENCE':
            self.root_ws().add_type_reference(self.name, self.implementation_type_ref)

    def get_array_length(self):
        """
        Deprecated, use arraySize property instead
        """
        return self.array_size

    @property
    def array_size(self):
        if len(self.sub_elements) > 0:
            return self.sub_elements[0].array_size
        else:
            return None

    def set_symbol_props(self, name: str, symbol: str):
        """
        Sets SymbolProps for this data type

        Arguments:
        name: <SHORT-NAME> (str)
        symbol: <SYMBOL> (str)
        """
        self.symbol_props = SymbolProps(name, symbol)


class SwBaseType(Element):
    @staticmethod
    def tag(*_):
        return 'SW-BASE-TYPE'

    def __init__(
            self,
            name: str,
            size: int | None = None,
            type_encoding: str | None = None,
            native_declaration: str | None = None,
            category: str = 'FIXED_LENGTH',
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data, category)
        self.size = size
        self.native_declaration = native_declaration
        self.type_encoding = type_encoding


class ImplementationDataTypeElement(Element, ImplementationDataTypeBase):
    @staticmethod
    def tag(*_):
        return 'IMPLEMENTATION-DATA-TYPE-ELEMENT'

    def __init__(
            self,
            name: str,
            category: str | None = None,
            array_size: int | str | None = None,
            array_size_semantics: str | None = None,
            variant_props: SwDataDefPropsConditional | SwPointerTargetProps | Iterable[SwDataDefPropsConditional | SwPointerTargetProps] | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data, category)
        self.array_size = array_size
        if array_size is not None:
            if array_size_semantics is not None:
                self.array_size_semantics = array_size_semantics
            else:
                self.array_size_semantics = 'FIXED-SIZE'
        else:
            self.array_size_semantics = None
        if variant_props is not None:
            if isinstance(variant_props, (SwDataDefPropsConditional, SwPointerTargetProps)):
                self.variant_props.append(variant_props)
            elif isinstance(variant_props, Iterable):
                for elem in variant_props:
                    if isinstance(elem, (SwDataDefPropsConditional, SwPointerTargetProps)):
                        self.variant_props.append(elem)
                    else:
                        raise ValueError('Invalid type: ', type(elem))
        ws = self.root_ws()
        if self.implementation_type_ref is not None:
            ws.add_type_reference(f'{self.parent.name}_{self.name}', self.implementation_type_ref)
        elif self.base_type_ref is not None:
            ws.add_type_reference(f'{self.parent.name}_{self.name}', self.base_type_ref)


class ApplicationDataType(Element):
    """
    Base type for AUTOSAR application data types (AUTOSAR4)

    Arguments:
    name: <SHORT-NAME> (None or str)
    variantProps: <SW-DATA-DEF-PROPS-VARIANTS> (instance (or list) of autosar.base.SwDataDefPropsConditional)
    category: <CATEGORY> (None or str)
    parent: parent object instance (usually the package it will belong to), (object)
    adminData: <ADMIN-DATA> (instance of autosar.base.AdminData or dict)
    """

    def __init__(
            self,
            name: str,
            variant_props: SwDataDefPropsConditional | Iterable[SwDataDefPropsConditional] | None = None,
            category: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data, category)
        self.variant_props: list[SwDataDefPropsConditional] = []
        if variant_props is not None:
            if isinstance(variant_props, SwDataDefPropsConditional):
                self.variant_props.append(variant_props)
            else:
                self.variant_props = list(variant_props)

    @property
    def compu_method_ref(self):
        if len(self.variant_props) > 0:
            return self.variant_props[0].compu_method_ref
        return None

    @property
    def data_constraint_ref(self):
        if len(self.variant_props) > 0:
            return self.variant_props[0].data_constraint_ref
        return None

    @property
    def unit_ref(self):
        if len(self.variant_props) > 0:
            return self.variant_props[0].unit_ref
        return None


class ApplicationPrimitiveDataType(ApplicationDataType):
    """
    Implementation of <APPLICATION-PRIMITIVE-DATA-TYPE> (AUTOSAR 4)

    Arguments:
    (see base class)
    """

    @staticmethod
    def tag(*_):
        return 'APPLICATION-PRIMITIVE-DATA-TYPE'

    def __init__(
            self,
            name: str,
            variant_props: SwDataDefPropsConditional | Iterable[SwDataDefPropsConditional] | None = None,
            category: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, variant_props, category, parent, admin_data)


class ApplicationArrayDataType(ApplicationDataType):
    """
    Implementation of <APPLICATION-ARRAY-DATA-TYPE> (AUTOSAR 4)

    Arguments:
    element: <ELEMENT> (instance of ApplicationArrayElement)
    """

    @staticmethod
    def tag(*_):
        return 'APPLICATION-ARRAY-DATA-TYPE'

    def __init__(
            self,
            name: str,
            element: 'ApplicationArrayElement | None',
            variant_props: SwDataDefPropsConditional | Iterable[SwDataDefPropsConditional] | None = None,
            category: str | None = 'ARRAY',
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, variant_props, category, parent, admin_data)
        if element is None or isinstance(element, ApplicationArrayElement):
            self.element = element
            element.parent = self
        else:
            raise ValueError('Element argument must be None or instance of ApplicationArrayElement')


class ApplicationArrayElement(Element):
    """
    An application array element (AUTOSAR 4).
    This is to be used as the element property of ApplicationArrayDataType.

    arguments:
    name: <SHORT-NAME> (None or str)
    typeRef: <TYPE-TREF> (None or str)
    arraySize: <MAX-NUMBER-OF-ELEMENTS> (None or int)
    sizeHandling: <ARRAY-SIZE-HANDLING> (None or str['ALL-INDICES-DIFFERENT-ARRAY-SIZE', 'ALL-INDICES-SAME-ARRAY-SIZE', 'INHERITED-FROM-ARRAY-ELEMENT-TYPE-SIZE', ])
    sizeSemantics: <ARRAY-SIZE-SEMANTICS> (None or str['FIXED-SIZE', 'VARIABLE-SIZE'])
    """

    @staticmethod
    def tag(*_):
        return 'ELEMENT'

    def __init__(
            self,
            name: str | None = None,
            type_ref: str | None = None,
            array_size: int | str | None = None,
            size_handling: str | None = None,
            size_semantics: str = 'FIXED-SIZE',
            category: str = 'VALUE',
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data, category)
        self.type_ref = type_ref
        self.array_size = int(array_size) if array_size is not None else None
        self.size_handling = size_handling
        self.size_semantics = size_semantics


class ApplicationRecordDataType(ApplicationDataType):
    """
    Implementation of <APPLICATION-RECORD-DATA-TYPE> (AUTOSAR 4)

    Arguments:
    elements: list of ApplicationRecordElement or None
    """

    @staticmethod
    def tag(*_):
        return 'APPLICATION-RECORD-DATA-TYPE'

    def __init__(
            self,
            name: str,
            elements: 'list[ApplicationRecordElement] | None' = None,
            variant_props: SwDataDefPropsConditional | Iterable[SwDataDefPropsConditional] | None = None,
            category: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, variant_props, category, parent, admin_data)
        if elements is None:
            elements = []
        self.elements: list[ApplicationRecordElement] = elements

    def append(self, element: 'ApplicationRecordElement'):
        """
        Append element to self.elements list
        """
        if not isinstance(element, ApplicationRecordElement):
            raise ValueError('Element must be an instance of ApplicationRecordElement')
        element.parent = self
        self.elements.append(element)

    def create_element(self, name: str, type_ref: str, category: str = 'VALUE', admin_data: AdminData | None = None):
        """
        Creates a new instance of ApplicationRecordElement and appends it to internal elements list
        """
        element = ApplicationRecordElement(name, type_ref, category, self, admin_data)
        self.elements.append(element)


class ApplicationRecordElement(Element):
    """
    Implements <APPLICATION-RECORD-ELEMENT> (AUTOSAR4)
    """

    @staticmethod
    def tag(*_):
        return 'APPLICATION-RECORD-ELEMENT'

    def __init__(
            self,
            name: str,
            type_ref: str,
            category: str = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data, category)
        if not isinstance(type_ref, str):
            raise InvalidDataTypeRef(type_ref)
        self.type_ref = type_ref


class DataTypeMappingSet(Element):
    @staticmethod
    def tag(*_):
        return 'DATA-TYPE-MAPPING-SET'

    def __init__(self, name: str, parent: ArObject | None = None, admin_data: AdminData | None = None):
        super().__init__(name, parent, admin_data)
        self.application_type_map: dict[str, str] = {}  # applicationDataTypeRef to implementationDataTypeRef dictionary
        self.mode_request_map: dict[str, str] = {}  # modeDeclarationGroupRef to implementationDataTypeRef dictionary

    def create_data_type_mapping(self, application_data_type_ref: str, implementation_data_type_ref: str):
        self.application_type_map[application_data_type_ref] = implementation_data_type_ref
        return DataTypeMap(application_data_type_ref, implementation_data_type_ref)

    def create_mode_request_mapping(self, mode_declaration_group_ref: str, implementation_data_type_ref: str):
        self.mode_request_map[mode_declaration_group_ref] = implementation_data_type_ref
        return ModeRequestTypeMap(mode_declaration_group_ref, implementation_data_type_ref)

    def add(self, item: 'DataTypeMap | ModeRequestTypeMap'):
        if isinstance(item, DataTypeMap):
            self.create_data_type_mapping(item.application_data_type_ref, item.implementation_data_type_ref)
        elif isinstance(item, ModeRequestTypeMap):
            self.create_mode_request_mapping(item.mode_declaration_group_ref, item.implementation_data_type_ref)
        else:
            raise ValueError("Item is neither an instance of DataTypeMap or ModeRequestTypeMap")

    def get_data_type_mapping(self, application_data_type_ref: str):
        """
        Returns an instance of DataTypeMap or None if not found.
        """
        implementation_data_type_ref = self.application_type_map.get(application_data_type_ref, None)
        if implementation_data_type_ref is not None:
            return DataTypeMap(application_data_type_ref, implementation_data_type_ref)
        return None

    def get_mode_request_mapping(self, mode_declaration_group_ref: str):
        """
        Returns an instance of DataTypeMap or None if not found.
        """
        implementation_data_type_ref = self.mode_request_map.get(mode_declaration_group_ref, None)
        if implementation_data_type_ref is not None:
            return ModeRequestTypeMap(mode_declaration_group_ref, implementation_data_type_ref)
        return None

    def find_mapped_data_type_ref(self, application_data_type_ref: str):
        """
        Returns a reference (str) to the mapped implementation data type or None if not found.
        """
        return self.application_type_map.get(application_data_type_ref, None)

    def find_mapped_data_type(self, application_data_type_ref: str):
        """
        Returns the instance of the mapped implementation data type.
        This requires that both the DataTypeMappingSet and the implementation data type reference are in the same AUTOSAR workspace.
        """
        implementation_data_type_ref = self.application_type_map.get(application_data_type_ref, None)
        if implementation_data_type_ref is not None:
            ws = self.root_ws()
            if ws is None:
                raise RuntimeError('Root workspace not found')
            return ws.find(implementation_data_type_ref)
        return None

    def find_mapped_mode_request_ref(self, mode_declaration_group_ref: str):
        """
        Returns a reference (str) to the mapped implementation data type or None if not found.
        """
        return self.mode_request_map.get(mode_declaration_group_ref, None)

    def find_mapped_mode_request(self, mode_declaration_group_ref: str):
        """
        Returns the instance of the mapped implementation data type.
        This requires that both the DataTypeMappingSet and the implementation data type reference are in the same AUTOSAR workspace.
        """
        implementation_data_type_ref = self.mode_request_map.get(mode_declaration_group_ref, None)
        if implementation_data_type_ref is not None:
            ws = self.root_ws()
            if ws is None:
                raise RuntimeError('Root workspace not found')
            return ws.find(implementation_data_type_ref)
        return None


class DataTypeMap:
    """
    Mapping from ApplicationDataType to ImplementationDataType.
    """

    def __init__(self, application_data_type_ref: str, implementation_data_type_ref: str):
        self.application_data_type_ref = application_data_type_ref
        self.implementation_data_type_ref = implementation_data_type_ref

    @staticmethod
    def tag(*_):
        return 'DATA-TYPE-MAP'


class ModeRequestTypeMap:
    """
    Mapping from ModeGroupDeclaration to ImplementationDataType.
    """

    def __init__(self, mode_declaration_group_ref: str, implementation_data_type_ref: str):
        self.mode_declaration_group_ref = mode_declaration_group_ref
        self.implementation_data_type_ref = implementation_data_type_ref

    @staticmethod
    def tag(*_):
        return 'MODE-REQUEST-TYPE-MAP'


class BufferComputation(ArObject):
    def __init__(
            self,
            offset: int | None = None,
            numerator: int | float | None = None,
            denominator: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if offset is None:
            offset = 0
        if numerator is None:
            numerator = 1
        if denominator is None or denominator == 0:
            denominator = 1
        self.offset = offset
        self.numerator = numerator
        self.denominator = denominator


class BufferProperties(ArObject):
    def __init__(
            self,
            buffer_computation: BufferComputation | None = None,
            header_length: int = 0,
            in_place: bool = False,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if buffer_computation is None:
            buffer_computation = BufferComputation()
        self.buffer_computation = buffer_computation
        self.header_length = header_length
        self.in_place = in_place
