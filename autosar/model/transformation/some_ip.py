from typing import Iterable

from autosar.model.enums import (
    SomeIpMessageTypeEnum,
    SomeIpTransformerSessionHandlingEnum,
    ByteOrderEnum,
)
from autosar.model.transformation.signal import (
    TransformationISignalPropsContent,
    AbstractTransformationISignalProps,
)
from autosar.model.transformation.sets import (
    AbstractTransformationDescription,
    AbstractTransformationProps,
)


class SomeIpTransformationISignalPropsContent(TransformationISignalPropsContent):
    def __init__(
            self,
            message_type: SomeIpMessageTypeEnum | None = None,
            interface_version: int | None = None,
            is_dynamic_length_field_size: bool | None = None,
            session_handling_sr: SomeIpTransformerSessionHandlingEnum | None = None,
            size_of_array_length_fields: int | None = None,
            size_of_string_length_fields: int | None = None,
            size_of_struct_length_fields: int | None = None,
            size_of_union_length_fields: int | None = None,
            tlv_data_id_definition_refs: Iterable[str] | None = None,
            implements_legacy_string_serialization: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.message_type = message_type
        self.interface_version = interface_version
        self.is_dynamic_length_field_size = is_dynamic_length_field_size
        self.session_handling_sr = session_handling_sr
        self.size_of_array_length_fields = size_of_array_length_fields
        self.size_of_string_length_fields = size_of_string_length_fields
        self.size_of_struct_length_fields = size_of_struct_length_fields
        self.size_of_union_length_fields = size_of_union_length_fields
        self.tlv_data_id_definition_refs = self.eval_children(tlv_data_id_definition_refs)
        self.implements_legacy_string_serialization = implements_legacy_string_serialization


class SomeIpTransformationISignalProps(
    AbstractTransformationISignalProps[SomeIpTransformationISignalPropsContent]
):
    pass


class SomeIpTransformationDescription(AbstractTransformationDescription):
    def __init__(
            self,
            interface_version: int,
            byte_order: ByteOrderEnum,
            alignment: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.interface_version = interface_version
        self.byte_order = byte_order
        self.alignment = alignment


class SomeIpTransformationProps(AbstractTransformationProps):
    def __init__(
            self,
            alignment: int | None = None,
            size_of_array_length_field: int | None = None,
            size_of_string_length_field: int | None = None,
            size_of_struct_length_field: int | None = None,
            size_of_union_length_field: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.alignment = alignment
        self.size_of_array_length_field = size_of_array_length_field
        self.size_of_string_length_field = size_of_string_length_field
        self.size_of_struct_length_field = size_of_struct_length_field
        self.size_of_union_length_field = size_of_union_length_field
