from dataclasses import dataclass

from autosar.ar_object import ArObject
from autosar.element import Element


class TransformationISignalProps(ArObject):
    pass


@dataclass
class SomeIpTransformationISignalProps(TransformationISignalProps):
    transformer_ref: str
    implements_some_ip_string_handling: bool
    message_type: str | None


@dataclass
class EndToEndTransformationISignalProps(TransformationISignalProps):
    transformer_ref: str
    data_ids: list[int] | None
    data_length: int | None

    def __post_init__(self):
        if self.data_ids is None:
            self.data_ids = []
        if self.data_length is None:
            self.data_length = 0


class SystemSignal(Element):
    def __init__(
            self,
            name: str,
            data_type_ref: str | None = None,
            init_value_ref: str | None = None,
            length: int | None = None,
            dynamic_length: bool = False,
            desc: str | None = None,
            parent: ArObject | None = None,
    ):
        super().__init__(name, parent)
        self.data_type_ref = data_type_ref
        self.init_value_ref = init_value_ref
        self.length = length
        self.dynamic_length = dynamic_length
        self.desc = desc
        self.parent = parent

    def asdict(self):
        data = {
            'type': self.__class__.__name__, 'name': self.name,
            'dataTypeRef': self.data_type_ref,
            'initValueRef': self.init_value_ref,
            'length': self.length,
        }
        if self.desc is not None:
            data['desc'] = self.desc
        return data


class SystemSignalGroup(Element):
    def __init__(
            self,
            name: str,
            system_signal_refs: list[str] | None = None,
            parent: ArObject | None = None,
    ):
        super().__init__(name, parent)
        if system_signal_refs is None:
            system_signal_refs = []
        self.system_signal_refs = system_signal_refs


class ISignal(Element):
    def __init__(
            self,
            data_type_policy: str,
            length: int,
            system_signal_ref: str,
            data_transformation_refs: list[str] | None = None,
            transformation_i_signal_props: list[TransformationISignalProps] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.data_type_policy = data_type_policy
        self.length = length
        self.system_signal_ref = system_signal_ref
        if data_transformation_refs is None:
            data_transformation_refs = []
        self.data_transformation_refs = data_transformation_refs
        if transformation_i_signal_props is None:
            transformation_i_signal_props = []
        self.transformation_i_signal_props = transformation_i_signal_props


class ISignalGroup(Element):
    def __init__(
            self,
            com_based_signal_group_transformations: list[str] | None = None,
            i_signal_refs: list[str] | None = None,
            system_signal_group_ref: str | None = None,
            transformation_i_signal_props: list[TransformationISignalProps] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.com_based_signal_group_transformations = com_based_signal_group_transformations
        if i_signal_refs is None:
            i_signal_refs = []
        self.i_signal_refs = i_signal_refs
        self.system_signal_group_ref = system_signal_group_ref
        if transformation_i_signal_props is None:
            transformation_i_signal_props = []
        self.transformation_i_signal_props = transformation_i_signal_props
