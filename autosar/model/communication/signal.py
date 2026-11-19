from dataclasses import dataclass
from typing import Iterable

from autosar.model.ar_object import ArObject
from autosar.model.base import Identifiable
from autosar.model.element import Element
from autosar.model.enums import DataTypePolicyEnum, ISignalTypeEnum, HandleOutOfRangeEnum
from autosar.model.sw_def_props import SwDataDefProps
from autosar.model.transformation.signal import TransformationISignalProps
from autosar.model.value_spec import ValueSpecification


@dataclass(repr=False)
class ISignalProps(ArObject):
    handle_out_of_range: HandleOutOfRangeEnum | None = None


class SystemSignal(Element):
    def __init__(
            self,
            dynamic_length: bool | None = None,
            physical_props: SwDataDefProps | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.dynamic_length = dynamic_length
        self.physical_props = physical_props


class SystemSignalGroup(Element):
    def __init__(
            self,
            system_signal_refs: Iterable[str] | None = None,
            transforming_system_signal_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.system_signal_refs = self.eval_children(system_signal_refs)
        self.transforming_system_signal_ref = transforming_system_signal_ref


class ISignal(Element):
    def __init__(
            self,
            system_signal_ref: str,
            length: int,
            data_type_policy: DataTypePolicyEnum,
            i_signal_type: ISignalTypeEnum | None = None,
            i_signal_props: ISignalProps | None = None,
            data_transformation_refs: Iterable[str] | None = None,
            init_value: ValueSpecification | None = None,
            network_representation_props: SwDataDefProps | None = None,
            reception_default_values: Iterable[ValueSpecification] | None = None,
            timeout_substitution_value: ValueSpecification | None = None,
            transformation_i_signal_props: Iterable[TransformationISignalProps] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.system_signal_ref = system_signal_ref
        self.length = length
        self.data_type_policy = data_type_policy
        self.i_signal_type = i_signal_type or ISignalTypeEnum.PRIMITIVE
        self.i_signal_props = i_signal_props
        self.data_transformation_refs = self.eval_children(data_transformation_refs)
        self.init_value = init_value
        self.network_representation_props = network_representation_props
        self.reception_default_values = self.eval_children(reception_default_values)
        self.timeout_substitution_value = timeout_substitution_value
        self.transformation_i_signal_props = self.eval_children(transformation_i_signal_props)


class ISignalGroup(Element):
    def __init__(
            self,
            system_signal_group_ref: str,
            i_signal_refs: Iterable[str] | None = None,
            com_based_sg_transform_refs: Iterable[str] | None = None,  # V+p
            transformation_i_signal_props: Iterable[TransformationISignalProps] | None = None,  # A+p
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.system_signal_group_ref = system_signal_group_ref
        self.i_signal_refs = self.eval_children(i_signal_refs)
        self.com_based_signal_group_transformation_refs = self.eval_children(com_based_sg_transform_refs)
        self.transformation_i_signal_props = self.eval_children(transformation_i_signal_props)


class ISignalTriggering(Identifiable):
    def __init__(
            self,
            i_signal_ref: str | None = None,
            i_signal_group_ref: str | None = None,
            i_signal_port_refs: Iterable[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.i_signal_ref = i_signal_ref
        self.i_signal_group_ref = i_signal_group_ref
        self.i_signal_port_refs = self.eval_children(i_signal_port_refs)
