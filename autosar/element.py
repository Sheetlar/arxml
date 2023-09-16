from typing import Any, Iterable, TypeVar

from autosar.ar_object import ArObject
from autosar.base import AdminData, SwDataDefPropsConditional, create_admin_data

T = TypeVar('T')


class Element(ArObject):
    def __init__(
            self,
            name: str | None,
            parent: ArObject | None = None,
            admin_data: AdminData | dict | None = None,
            category: str | None = None,
            desc: str | None = None,
            long_name: str | None = None,
    ):
        super().__init__()
        if isinstance(admin_data, dict):
            admin_data_obj = create_admin_data(admin_data)
        else:
            admin_data_obj = admin_data
        if (admin_data_obj is not None) and not isinstance(admin_data_obj, AdminData):
            raise ValueError('adminData must be of type dict or autosar.base.AdminData')
        self.name = name
        self.desc = desc
        self.long_name = long_name
        self.admin_data = admin_data_obj
        self.category = category
        self._parent = parent
        self._find_sets: list[list[Element] | None] = []

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, obj: ArObject):
        self._parent = obj
        self._set_children_parent()

    def _set_children_parent(self):
        pass

    def find(self, ref: str, role: str | None = None):
        name, _, tail = ref.partition('/')
        for subset in self._find_sets:
            if subset is None:
                continue
            for element in subset:
                if element.name == name:
                    if len(tail) > 0:
                        return element.find(tail)
                    return element
        ws = self.root_ws()
        return ws.find(ref, role)

    @property
    def ref(self):
        if self.parent is not None and self.name is not None:
            return f'{self.parent.ref}/{self.name}'
        return None

    def root_ws(self):
        if self.parent is None:
            return None
        return self.parent.root_ws()

    def __deepcopy__(self, memo):
        raise NotImplementedError(type(self))

    def _set_parent(self, sub_elements: Iterable[T] | None, parent: ArObject | None = None) -> list[T]:
        if sub_elements is None:
            return []
        if parent is None:
            parent = self
        if not isinstance(sub_elements, list):
            sub_elements = list(sub_elements)
        for sub_element in sub_elements:
            sub_element.parent = parent
        return sub_elements


class LabelElement(ArObject):
    """Same as Element but uses label as main identifier instead of name"""

    def __init__(
            self,
            label: str,
            parent: ArObject | None = None,
            admin_data: AdminData | dict | None = None,
            category: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if isinstance(admin_data, dict):
            admin_data_obj = create_admin_data(admin_data)
        else:
            admin_data_obj = admin_data
        if (admin_data_obj is not None) and not isinstance(admin_data_obj, AdminData):
            raise ValueError('adminData must be of type dict or autosar.base.AdminData')
        self.label = label
        self.admin_data = admin_data_obj
        self.parent = parent
        self.category = category

    @property
    def ref(self):
        if self.parent is not None:
            return f'{self.parent.ref}/{self.label}'
        else:
            return None

    def root_ws(self):
        if self.parent is None:
            return None
        else:
            return self.parent.root_ws()


class DataElement(Element):
    @staticmethod
    def tag(version: float):
        return "VARIABLE-DATA-PROTOTYPE" if version >= 4.0 else "DATA-ELEMENT-PROTOTYPE"

    def __init__(
            self,
            name: str,
            type_ref: str,
            is_queued: bool = False,
            sw_address_method_ref: str | None = None,
            sw_calibration_access: str | None = None,
            sw_impl_policy: str | None = None,
            category: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data, category)
        if isinstance(type_ref, str):
            self.type_ref = type_ref
        elif hasattr(type_ref, 'ref'):
            assert (isinstance(type_ref.ref, str))
            self.type_ref = type_ref.ref
        else:
            raise ValueError('Unsupported type for argument: typeRef')
        assert (isinstance(is_queued, bool))
        self._sw_impl_policy = sw_impl_policy
        self.is_queued = is_queued
        self.sw_address_method_ref = sw_address_method_ref
        self.sw_calibration_access = sw_calibration_access
        self.data_constraint_ref = None
        if self.sw_impl_policy is None and self.is_queued:
            self.sw_impl_policy = 'QUEUED'

    @property
    def sw_impl_policy(self):
        return self._sw_impl_policy

    @sw_impl_policy.setter
    def sw_impl_policy(self, value: str | None):
        if value is None:
            self._sw_impl_policy = None
        else:
            uc_value = value.upper()
            enum_values = ['CONST', 'FIXED', 'MEASUREMENT-POINT', 'QUEUED', 'STANDARD']
            if uc_value in enum_values:
                self._sw_impl_policy = uc_value
                if uc_value == 'QUEUED':
                    self.is_queued = True
            else:
                raise ValueError(f'Invalid swImplPolicy value: {value}')

    def set_props(self, props: SwDataDefPropsConditional):
        if isinstance(props, SwDataDefPropsConditional):
            self.sw_calibration_access = props.sw_calibration_access
            self.sw_address_method_ref = props.sw_address_method_ref
            self.sw_impl_policy = props.sw_impl_policy
            self.data_constraint_ref = props.data_constraint_ref
        else:
            raise NotImplementedError(type(props))


class ParameterDataPrototype(Element):
    """
    Represents <PARAMETER-DATA-PROTOTYPE> (AUTOSAR 4)
    Or
    Represents <CALPRM-ELEMENT-PROTOTYPE> (AUTOSAR 3)
    """

    def __init__(
            self,
            name: str,
            type_ref: str,
            sw_address_method_ref: str | None = None,
            sw_calibration_access: str | None = None,
            init_value: Any = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.type_ref = type_ref
        self.sw_address_method_ref = sw_address_method_ref
        self.sw_calibration_access = sw_calibration_access
        self.init_value = init_value

    @staticmethod
    def tag(version: float):
        return "PARAMETER-DATA-PROTOTYPE" if version >= 4.0 else "CALPRM-ELEMENT-PROTOTYPE"


class SoftwareAddressMethod(Element):
    """
    Represents <SW-ADDR-METHOD> (AUTOSAR 3) (AUTOSAR 4)
    """

    def __init__(self, name: str, parent: ArObject | None = None, admin_data: AdminData | None = None):
        super().__init__(name, parent, admin_data)

    @staticmethod
    def tag(*_):
        return 'SW-ADDR-METHOD'
