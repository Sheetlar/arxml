from typing import TypeAlias

from autosar import ArObject
from autosar.model.atp_variation import Variants
from autosar.model.base import Describable, SwDataDefPropsVariants, ValueSpecification
from autosar.model.element import Element


class ISignalProps(ArObject):
    def __init__(
            self,
            handle_out_of_range: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.handle_out_of_range = handle_out_of_range


class TransformationISignalProps(Describable):
    def __init__(
            self,
            transformer_ref: str,
            cs_error_reaction: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.transformer_ref = transformer_ref
        self.cs_error_reaction = cs_error_reaction


class EndToEndTransformationISignalProps(TransformationISignalProps):
    def __init__(
            self,
            data_ids: list[int] | None = None,
            data_length: int | None = None,
            max_data_length: int | None = None,
            min_data_length: int | None = None,
            source_id: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if data_ids is None:
            data_ids = []
        if data_length is None:
            data_length = 0
        self.data_ids = data_ids
        self.data_length = data_length
        self.max_data_length = max_data_length
        self.min_data_length = min_data_length
        self.source_id = source_id


class EndToEndTransformationISignalPropsVariants(Variants[EndToEndTransformationISignalProps]):
    pass


class SomeIpTransformationISignalProps(TransformationISignalProps):
    def __init__(
            self,
            message_type: str | None = None,
            interface_version: int | None = None,
            is_dynamic_length_field_size: bool | None = None,
            session_handling_sr: str | None = None,
            size_of_array_length_fields: int | None = None,
            size_of_string_length_fields: int | None = None,
            size_of_struct_length_fields: int | None = None,
            size_of_union_length_fields: int | None = None,
            tlv_data_id_definition_refs: list[str] | None = None,
            implements_legacy_string_serialization: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if tlv_data_id_definition_refs is None:
            tlv_data_id_definition_refs = []
        self.message_type = message_type
        self.interface_version = interface_version
        self.is_dynamic_length_field_size = is_dynamic_length_field_size
        self.session_handling_sr = session_handling_sr
        self.size_of_array_length_fields = size_of_array_length_fields
        self.size_of_string_length_fields = size_of_string_length_fields
        self.size_of_struct_length_fields = size_of_struct_length_fields
        self.size_of_union_length_fields = size_of_union_length_fields
        self.tlv_data_id_definition_refs = tlv_data_id_definition_refs
        self.implements_legacy_string_serialization = implements_legacy_string_serialization


class SomeIpTransformationISignalPropsVariants(Variants[SomeIpTransformationISignalProps]):
    pass


class UserDefinedTransformationISignalProps(TransformationISignalProps):
    pass


class UserDefinedTransformationISignalPropsVariants(Variants[UserDefinedTransformationISignalProps]):
    pass


TransformationISignalPropsVariants: TypeAlias = (
        EndToEndTransformationISignalPropsVariants |
        SomeIpTransformationISignalPropsVariants |
        UserDefinedTransformationISignalPropsVariants
)


class SystemSignal(Element):
    def __init__(
            self,
            dynamic_length: bool | None = None,
            physical_props: SwDataDefPropsVariants | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.dynamic_length = dynamic_length
        self.physical_props = physical_props


class SystemSignalGroup(Element):
    def __init__(
            self,
            system_signal_refs: list[str] | None = None,
            transforming_system_signal_ref: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if system_signal_refs is None:
            system_signal_refs = []
        self.system_signal_refs = system_signal_refs
        self.transforming_system_signal_ref = transforming_system_signal_ref


class ISignal(Element):
    def __init__(
            self,
            system_signal_ref: str,
            data_type_policy: str,
            length: int,
            i_signal_type: str | None = None,
            i_signal_props: ISignalProps | None = None,
            data_transformation_refs: list[str] | None = None,
            init_value: ValueSpecification | None = None,
            network_representation_props: SwDataDefPropsVariants | None = None,
            timeout_substitution_value: ValueSpecification | None = None,
            transformation_i_signal_props: list[TransformationISignalPropsVariants] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if i_signal_type is None:
            i_signal_type = 'PRIMITIVE'
        if data_transformation_refs is None:
            data_transformation_refs = []
        if transformation_i_signal_props is None:
            transformation_i_signal_props = []
        self.system_signal_ref = system_signal_ref
        self.data_type_policy = data_type_policy
        self.length = length
        self.i_signal_type = i_signal_type
        self.i_signal_props = i_signal_props
        self.data_transformation_refs = data_transformation_refs
        self.init_value = init_value
        self.network_representation_props = network_representation_props
        self.timeout_substitution_value = timeout_substitution_value
        self.transformation_i_signal_props = transformation_i_signal_props


class ISignalGroup(Element):
    def __init__(
            self,
            i_signal_refs: list[str] | None = None,
            system_signal_group_ref: str | None = None,
            com_based_signal_group_transformation_refs: list[str] | None = None,
            transformation_i_signal_props: list[TransformationISignalPropsVariants] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if i_signal_refs is None:
            i_signal_refs = []
        if com_based_signal_group_transformation_refs is None:
            com_based_signal_group_transformation_refs = []
        if transformation_i_signal_props is None:
            transformation_i_signal_props = []
        self.i_signal_refs = i_signal_refs
        self.system_signal_group_ref = system_signal_group_ref
        self.com_based_signal_group_transformation_refs = com_based_signal_group_transformation_refs
        self.transformation_i_signal_props = transformation_i_signal_props
