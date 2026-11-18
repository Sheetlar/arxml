from dataclasses import dataclass, field

from autosar.model.ar_object import ArObject


class AtpInstanceRef(ArObject):
    """Abstract"""


@dataclass(repr=False)
class AnyInstanceRef(AtpInstanceRef):
    base_ref: str | None = None
    context_element_refs: list[str] = field(default_factory=list)
    target_ref: str | None = None


@dataclass(repr=False)
class ComponentInSystemInstanceRef(AtpInstanceRef):
    base_ref: str | None = None
    context_composition_ref: str | None = None
    context_component_refs: list[str] = field(default_factory=list)
    target_component_ref: str | None = None


@dataclass(repr=False)
class DataPrototypeInSystemInstanceRef(AtpInstanceRef):
    base_ref: str | None = None
    context_root_composition_ref: str | None = None
    context_component_refs: list[str] = field(default_factory=list)
    context_port_ref: str | None = None
    root_data_prototype_ref: str | None = None
    context_data_prototype_refs: list[str] = field(default_factory=list)
    target_data_prototype_ref: str | None = None


@dataclass(repr=False)
class DataPrototypeInClientServerInterfaceInstanceRef(AtpInstanceRef):
    base_ref: str | None = None
    root_data_prototype_in_cs_ref: str | None = None
    context_data_prototype_in_cs_refs: list[str] = field(default_factory=list)
    target_data_prototype_in_cs_ref: str | None = None


@dataclass(repr=False)
class DataPrototypeInSenderReceiverInterfaceInstanceRef(AtpInstanceRef):
    base_ref: str | None = None
    root_data_prototype_in_sr_ref: str | None = None
    context_data_prototype_in_sr_refs: list[str] = field(default_factory=list)
    target_data_prototype_in_sr_ref: str | None = None


@dataclass(repr=False)
class OperationInSystemInstanceRef(AtpInstanceRef):
    base_ref: str | None = None
    context_composition_ref: str | None = None
    context_component_refs: list[str] = field(default_factory=list)
    context_port_ref: str | None = None
    target_operation_ref: str | None = None


@dataclass(repr=False)
class VariableDataPrototypeInSystemInstanceRef(AtpInstanceRef):
    base_ref: str | None = None
    context_composition_ref: str | None = None
    context_component_refs: list[str] = field(default_factory=list)
    context_port_ref: str | None = None
    target_data_prototype_ref: str | None = None


@dataclass(repr=False)
class PortGroupInSystemInstanceRef(AtpInstanceRef):
    base_ref: str | None = None
    context_composition_ref: str | None = None
    context_component_refs: list[str] = field(default_factory=list)
    target_ref: str | None = None


@dataclass(repr=False)
class TriggerInSystemInstanceRef(AtpInstanceRef):
    base_ref: str | None = None
    context_composition_ref: str | None = None
    context_component_refs: list[str] = field(default_factory=list)
    context_port_ref: str | None = None
    target_trigger_ref: str | None = None
