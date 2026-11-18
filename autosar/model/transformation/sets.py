from dataclasses import dataclass
from typing import TypeVar, Iterable

from autosar.model.ar_object import ArObject
from autosar.model.base import Describable, Identifiable
from autosar.model.compu import CompuScale
from autosar.model.element import Element
from autosar.model.enums import DataTransformationKindEnum, TransformerClassEnum


@dataclass(repr=False)
class BufferProperties(ArObject):
    header_length: int
    in_place: bool
    buffer_computation: CompuScale | None = None


class AbstractTransformationDescription(Describable):
    """Abstract"""


TransformationDescription = TypeVar('TransformationDescription', bound=AbstractTransformationDescription)


class TransformationTechnology(Identifiable):
    def __init__(
            self,
            protocol: str,
            version: str,
            transformer_class: TransformerClassEnum,
            buffer_properties: BufferProperties,
            has_internal_state: bool | None = None,
            needs_original_data: bool | None = None,
            transformation_descriptions: Iterable[TransformationDescription] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.protocol = protocol
        self.version = version
        self.transformer_class = transformer_class
        self.buffer_properties = buffer_properties
        self.has_internal_state = has_internal_state
        self.needs_original_data = needs_original_data
        self.transformation_descriptions = self.eval_children(transformation_descriptions)


class DataTransformation(Identifiable):
    def __init__(
            self,
            transformer_chain_refs: Iterable[str],
            execute_despite_data_unavailability: bool,
            data_transformation_kind: DataTransformationKindEnum | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.transformer_chain_refs = self.eval_children(transformer_chain_refs)
        self.execute_despite_data_unavailability = execute_despite_data_unavailability
        self.data_transformation_kind = data_transformation_kind


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

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.data_transformations
        yield from self.transformation_technologies


class AbstractTransformationProps(Identifiable):
    pass


TransformationProps = TypeVar('TransformationProps', bound=AbstractTransformationProps)


class TransformationPropsSet(Element):
    def __init__(
            self,
            transformation_props: Iterable[TransformationProps] | None = None,  # A
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.transformation_props = self._set_parent(transformation_props)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.transformation_props
