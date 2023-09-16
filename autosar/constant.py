from typing import Iterable

from autosar.ar_object import ArObject
from autosar.base import AdminData
from autosar.element import Element, LabelElement


def initializer_string(constant: 'IntegerValue | RecordValue'):
    if constant is None:
        return ''
    elif isinstance(constant, IntegerValue):
        return str(constant.value)
    elif isinstance(constant, RecordValue):
        prolog = '{'
        epilog = '}'
        values = ', '.join(initializer_string(elem) for elem in constant.elements)
        return f'{prolog}{values}{epilog}'
    else:
        raise NotImplementedError(str(type(constant)))


class Value(Element):
    def __init__(self, name: str, parent: ArObject | None = None, admin_data: AdminData | None = None, category: str | None = None):
        super().__init__(name, parent, admin_data, category)
        self.type_ref: str | None = None


class ValueAR4(LabelElement):
    """Same as Value but uses label as main identifier instead of name"""

    def __init__(self, label: str, parent: ArObject | None = None, admin_data: AdminData | None = None, category: str | None = None):
        super().__init__(label, parent, admin_data, category)


# AUTOSAR 3 constant values
class IntegerValue(Value):
    @staticmethod
    def tag(*_):
        return 'INTEGER-LITERAL'

    def __init__(self, name: str, type_ref: str | None = None, value: int | None = None, parent: ArObject | None = None):
        super().__init__(name, parent)
        self.type_ref = type_ref
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val: int | None):
        if val is not None:
            self._value = int(val)
        else:
            self._value = None


class StringValue(Value):
    @staticmethod
    def tag(*_):
        return 'STRING-LITERAL'

    def __init__(self, name: str, type_ref: str | None = None, value: str | None = None, parent: ArObject | None = None):
        super().__init__(name, parent)
        if value is None:
            value = ''
        assert (isinstance(value, str))
        self.type_ref = type_ref
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val: str | None):
        if val is not None:
            self._value = str(val)
        else:
            self._value = None


class BooleanValue(Value):
    @staticmethod
    def tag(*_):
        return 'BOOLEAN-LITERAL'

    def __init__(self, name: str, type_ref: str | None = None, value: int | None = None, parent: ArObject | None = None):
        super().__init__(name, parent)
        self.type_ref = type_ref
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val: str | int | None):
        if val is not None:
            if isinstance(val, str):
                self._value = True if val == 'true' else False
            else:
                self._value = bool(val)
        else:
            self._value = None


class RecordValue(Value):
    """
    typeRef is only necessary for AUTOSAR 3 constants
    """

    @staticmethod
    def tag(version: float | None = None):
        if version is not None and version >= 4.0:
            return 'RECORD-VALUE-SPECIFICATION'
        return 'RECORD-SPECIFICATION'

    def __init__(self, name: str, type_ref: str | None = None, elements: Iterable | None = None, parent: ArObject | None = None):
        super().__init__(name, parent)
        self.type_ref = type_ref
        if elements is None:
            self.elements = []
        else:
            self.elements = list(elements)


class ArrayValue(Value):
    """
    name and typeRef is only necessary for AUTOSAR 3 constants
    """

    @staticmethod
    def tag(version: float | None = None):
        if version is not None and version >= 4.0:
            return 'ARRAY-VALUE-SPECIFICATION'
        return 'ARRAY-SPECIFICATION'

    def __init__(self, name: str, type_ref: str | None = None, elements: Iterable | None = None, parent: ArObject | None = None):
        super().__init__(name, parent)
        self.type_ref = type_ref
        if elements is None:
            self.elements = []
        else:
            self.elements = list(elements)


# AUTOSAR 4 constant values
class TextValue(ValueAR4):
    @staticmethod
    def tag(*_):
        return "TEXT-VALUE-SPECIFICATION"

    def __init__(
            self,
            label: str,
            value: str | None = None,
            category: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(label, parent, admin_data, category)
        if value is None:
            value = ''
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val: str | None):
        if val is not None:
            self._value = val
        else:
            self._value = None


class NumericalValue(ValueAR4):
    @staticmethod
    def tag(*_):
        return "NUMERICAL-VALUE-SPECIFICATION"

    def __init__(
            self,
            label: str,
            value: int | float | None = None,
            category: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(label, parent, admin_data, category)
        if value is None:
            value = 0
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if val is not None:
            self._value = str(val)
        else:
            self._value = None


class ApplicationValue(ValueAR4):
    """
    (AUTOSAR4)
    Implements <APPLICATION-VALUE-SPECIFICATION>
    """

    @staticmethod
    def tag(*_):
        return "APPLICATION-VALUE-SPECIFICATION"

    def __init__(
            self,
            label: str | None = None,
            sw_value_cont: 'SwValueCont | None' = None,
            sw_axis_cont: 'SwAxisCont | None' = None,
            category: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(label, parent, admin_data, category)
        if (sw_axis_cont is not None) and (not isinstance(sw_axis_cont, SwAxisCont)):
            raise ValueError('swAxisCont argument must be None or instance of SwAxisCont')
        if (sw_value_cont is not None) and (not isinstance(sw_value_cont, SwValueCont)):
            raise ValueError('swValueCont argument must be None or instance of SwValueCont')
        self.sw_axis_cont = sw_axis_cont
        self.sw_value_cont = sw_value_cont


class ConstantReference(ValueAR4):
    """
    Container class for <CONSTANT-REFERENCE> (AUTOSAR 4)
    """

    @staticmethod
    def tag(*_):
        return 'CONSTANT-REFERENCE'

    def __init__(
            self,
            label: str | None = None,
            value: str | None = None,
            category: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(label, parent, admin_data, category)
        self.value = value


class RecordValueAR4(ValueAR4):
    @staticmethod
    def tag(*_):
        return "RECORD-VALUE-SPECIFICATION"

    def __init__(
            self,
            label: str,
            type_ref: str | None = None,
            elements: Iterable | None = None,
            category: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(label, parent, admin_data, category)
        self.type_ref = type_ref
        if elements is None:
            self.elements = []
        else:
            self.elements = list(elements)


class ArrayValueAR4(ValueAR4):
    @staticmethod
    def tag(*_):
        return "ARRAY-VALUE-SPECIFICATION"

    def __init__(
            self,
            label: str,
            type_ref: str | None = None,
            elements: Iterable | None = None,
            category: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(label, parent, admin_data, category)
        self.type_ref = type_ref
        if elements is None:
            self.elements = []
        else:
            self.elements = list(elements)


# Common classes
class Constant(Element):
    @staticmethod
    def tag(*_):
        return 'CONSTANT-SPECIFICATION'

    def __init__(self, name: str, value: Value | ValueAR4 | None = None, parent: ArObject | None = None, admin_data: AdminData | None = None):
        super().__init__(name, parent, admin_data)
        self.value = value
        if value is not None:
            value.parent = self

    def find(self, ref: str, *_):
        if self.value.name == ref:
            return self.value
        return None


class SwValueCont:
    """
    (AUTOSAR4)
    Implements <SW-VALUE-CONT>
    """

    @staticmethod
    def tag(*_):
        return 'SW-VALUE-CONT'

    def __init__(
            self,
            values: str | int | float | list | None = None,
            unit_ref: str | None = None,
            unit_display_name: str | None = None,
            sw_array_size: int | None = None,
    ):
        self.values = values
        self.unit_ref = unit_ref
        self.unit_display_name = unit_display_name
        self.sw_array_size = sw_array_size


class SwAxisCont:
    """
    (AUTOSAR4)
    Implements <SW-AXIS-CONT>
    """

    @staticmethod
    def tag(*_):
        return 'SW-AXIS-CONT'

    def __init__(
            self,
            values: str | int | float | list | None = None,
            unit_ref: str | None = None,
            unit_display_name: str | None = None,
            sw_axis_index: int | None = None,
            sw_array_size: int | None = None,
            category: str | None = None,
    ):
        self.unit_ref = unit_ref
        self.unit_display_name = unit_display_name
        self.sw_axis_index = sw_axis_index
        self.sw_array_size = sw_array_size
        self.category = category
        self.values = values
