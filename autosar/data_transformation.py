from dataclasses import dataclass
from typing import Iterable

from autosar.datatype import BufferProperties
from autosar.element import Element


class TransformationDescription(Element):
    pass


@dataclass
class SomeIpTransformationDescription(TransformationDescription):
    alignment: int | None = None
    byte_order: str | None = None
    interface_version: int | None = None


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


class DataTransformation(Element):
    def __init__(
            self,
            execute_despite_data_unavailability: bool = False,
            transformer_chain_refs: list[str] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.execute_despite_data_unavailability = execute_despite_data_unavailability
        if transformer_chain_refs is None:
            transformer_chain_refs = []
        self.transformer_chain_refs = transformer_chain_refs


class TransformationTechnology(Element):
    def __init__(
            self,
            buffer_properties: BufferProperties | None = None,
            has_internal_state: bool = False,
            needs_original_data: bool = False,
            protocol: str | None = None,
            transformer_class: str | None = None,
            version: int | None = None,
            transformation_descriptions: list[TransformationDescription] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.buffer_properties = buffer_properties
        self.has_internal_state = has_internal_state
        self.needs_original_data = needs_original_data
        self.protocol = protocol
        self.transformer_class = transformer_class
        self.version = version
        if transformation_descriptions is None:
            transformation_descriptions = []
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
        self._find_sets = [self.data_transformations, self.transformation_technologies]
