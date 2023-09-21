from abc import (ABC, abstractmethod)
from typing import Any

from autosar.ar_object import ArObject
from autosar.base import split_ref as ar_split_ref, AdminData
from autosar.element import DataElement, ParameterDataPrototype
from autosar.mode import ModeGroup
from autosar.portinterface import ApplicationError
from autosar.workspace import Workspace


def workspace(
        version: float = 3.0,
        patch: int = 2,
        schema: str | None = None,
        attributes: Any = None,
):
    if schema is None and ((version == 3.0 and patch == 2) or (version == "3.0.2")):
        schema = 'autosar_302_ext.xsd'
    return Workspace(version, patch, schema, attributes)


def split_ref(ref: str):
    return ar_split_ref(ref)


def data_element(
        name: str,
        type_ref: str,
        is_queued: bool = False,
        software_address_method_ref: str | None = None,
        sw_calibration_access: str | None = None,
        sw_impl_policy: str | None = None,
        parent: ArObject | None = None,
        admin_data: AdminData | None = None,
):
    return DataElement(name, type_ref, is_queued, software_address_method_ref, sw_calibration_access, sw_impl_policy, parent, admin_data)


def application_error(
        name: str,
        error_code: int,
        parent: ArObject | None = None,
        admin_data: AdminData | None = None,
):
    return ApplicationError(name, error_code, parent, admin_data)


def mode_group(
        name: str,
        type_ref: str,
        parent: ArObject | None = None,
        admin_data: AdminData | None = None,
):
    return ModeGroup(name, type_ref, parent, admin_data)


def parameter_data_prototype(
        name: str,
        type_ref: str,
        sw_address_method_ref: str | None = None,
        sw_calibration_access: str | None = None,
        init_value: Any = None,
        parent: ArObject | None = None,
        admin_data: AdminData | None = None,
):
    return ParameterDataPrototype(name, type_ref, sw_address_method_ref, sw_calibration_access, init_value, parent, admin_data)


# template support
class Template(ABC):
    usage_count = 0  # number of times this template have been applied
    static_ref = ''

    @classmethod
    def ref(cls, ws):
        return cls.static_ref

    @classmethod
    def get(cls, ws):
        ref = cls.ref(ws)
        if ws.find(ref) is None:
            ws.apply(cls)
        return ws.find(ref)

    @classmethod
    @abstractmethod
    def apply(cls, ws, **kwargs):
        """
        Applies this class template to the workspace ws
        """
