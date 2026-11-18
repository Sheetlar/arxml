from dataclasses import dataclass, field
from typing import TypeVar, Iterable

from autosar.model.ar_object import ArObject, ArObjectWithParent
from autosar.model.atp_variation import PropertySet
from autosar.model.base import Describable, Identifiable
from autosar.model.enums import CSTransformerErrorReactionEnum
from autosar.model.instance_ref import (
    DataPrototypeInClientServerInterfaceInstanceRef,
    DataPrototypeInSenderReceiverInterfaceInstanceRef,
)
from autosar.model.sw_def_props import SwDataDefProps


class AbstractDataPrototypeReference(ArObject):
    """Abstract"""


@dataclass(repr=False)
class DataPrototypeInPortInterfaceRef(AbstractDataPrototypeReference):
    data_prototype_in_client_server_interface: DataPrototypeInClientServerInterfaceInstanceRef | None = None  # TAG
    data_prototype_in_sender_receiver_interface: DataPrototypeInSenderReceiverInterfaceInstanceRef | None = None  # TAG


@dataclass(repr=False)
class ImplementationDataTypeElementInPortInterfaceRef(AbstractDataPrototypeReference):
    root_data_prototype_ref: str | None = None
    context_implementation_data_element_refs: list[str] = field(default_factory=list)
    target_implementation_data_type_element_ref: str | None = None


DataPrototypeReference = TypeVar('DataPrototypeReference', bound=AbstractDataPrototypeReference)


class DataPrototypeTransformationPropsIdent(Identifiable):
    pass


@dataclass(repr=False)
class DataPrototypeTransformationProps(ArObjectWithParent):
    data_prototype_in_port_interface_ref: DataPrototypeReference | None = None  # type: ignore
    network_representation_props: SwDataDefProps | None = None
    transformation_props_ref: str | None = None
    ident: DataPrototypeTransformationPropsIdent | None = None

    def __post_init__(self):
        if self.ident is not None:
            self.ident.parent = self


class TransformationISignalPropsIdent(Identifiable):
    pass


class TransformationISignalPropsContent(ArObjectWithParent):
    def __init__(
            self,
            transformer_ref: str | None = None,
            cs_error_reaction: CSTransformerErrorReactionEnum | None = None,
            data_prototype_transformation_props: Iterable[DataPrototypeTransformationProps] | None = None,
            ident: TransformationISignalPropsIdent | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if ident is not None:
            ident.parent = self
        self.transformer_ref = transformer_ref
        self.cs_error_reaction = cs_error_reaction
        self.data_prototype_transformation_props = self._set_parent(data_prototype_transformation_props)
        self.ident = ident

    @property
    def identifiables(self) -> Iterable[ArObject]:
        if self.ident is not None:
            yield self.ident
        yield from (
            p.ident
            for p in self.data_prototype_transformation_props
            if p.ident is not None
        )


C = TypeVar('C', bound=TransformationISignalPropsContent)


class AbstractTransformationISignalProps(Describable, PropertySet[C]):
    """Abstract"""

    @property
    def identifiables(self) -> Iterable[ArObject]:
        for v in self.variants:
            yield from v.identifiables


TransformationISignalProps = TypeVar('TransformationISignalProps', bound=AbstractTransformationISignalProps)
