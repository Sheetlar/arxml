from dataclasses import dataclass
from typing import Iterable, TypeVar

from autosar import ArObject
from autosar.model.base import Describable
from autosar.model.compu import CompuScale
from autosar.model.element import Element


@dataclass
class BufferProperties(ArObject):
    header_length: int
    in_place: bool
    buffer_computation: CompuScale | None = None


class TransformationDescription(Describable):
    pass


@dataclass
class EndToEndTransformationDescription(TransformationDescription):
    counter_offset: int | None = None
    crc_offset: int | None = None
    offset: int | None = None
    data_id_model: str | None = None
    e2e_profile_compatibility_props_ref: str | None = None
    max_delta_counter: int | None = None
    max_error_state_init: int | None = None
    max_error_state_invalid: int | None = None
    max_error_state_valid: int | None = None
    max_no_new_or_repeated_data: int | None = None
    min_ok_state_init: int | None = None
    min_ok_state_invalid: int | None = None
    min_ok_state_valid: int | None = None
    profile_behavior: str | None = None
    profile_name: str | None = None
    sync_counter_init: int | None = None
    upper_header_bits_to_shift: int | None = None
    window_size_init: int | None = None
    window_size_invalid: int | None = None
    window_size_valid: int | None = None


@dataclass
class SomeIpTransformationDescription(TransformationDescription):
    alignment: int | None = None
    byte_order: str | None = None
    interface_version: int | None = None


class UserDefinedTransformationDescription(TransformationDescription):
    pass


AnyTransformationDescription = TypeVar('AnyTransformationDescription', bound=TransformationDescription)


class DataTransformation(Element):
    def __init__(
            self,
            transformer_chain_refs: list[str],
            execute_despite_data_unavailability: bool,
            data_transformation_kind: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if transformer_chain_refs is None:
            transformer_chain_refs = []
        self.transformer_chain_refs = transformer_chain_refs
        self.execute_despite_data_unavailability = execute_despite_data_unavailability
        self.data_transformation_kind = data_transformation_kind


class TransformationTechnology(Element):
    def __init__(
            self,
            protocol: str,
            version: str,
            transformer_class: str,
            buffer_properties: BufferProperties,
            has_internal_state: bool = False,
            needs_original_data: bool = False,
            transformation_descriptions: list[AnyTransformationDescription] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if transformation_descriptions is None:
            transformation_descriptions = []
        self.protocol = protocol
        self.version = version
        self.transformer_class = transformer_class
        self.buffer_properties = buffer_properties
        self.has_internal_state = has_internal_state
        self.needs_original_data = needs_original_data
        self.transformation_descriptions = transformation_descriptions


class DataTransformationSet(Element):
    def __init__(
            self,
            data_transformations: Iterable[DataTransformation] | None = None,
            transformation_technologies: Iterable[TransformationTechnology] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.data_transformations = self._set_parent(data_transformations)
        self.transformation_technologies = self._set_parent(transformation_technologies)
        self._find_sets = (self.data_transformations, self.transformation_technologies)


class TransformationProps(Element):
    pass


class SOMEIPTransformationProps(TransformationProps):
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


class UserDefinedTransformationProps(TransformationProps):
    pass


AnyTransformationProps = TypeVar('AnyTransformationProps', bound=TransformationProps)


class TransformationPropsSet(Element):
    def __init__(
            self,
            transformation_props: Iterable[AnyTransformationProps] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.transformation_props = self._set_parent(transformation_props)
        self._find_sets = (self.transformation_props,)
