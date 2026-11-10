from dataclasses import dataclass, field
from typing import TypeVar

from autosar.model.ar_object import ArObject
from autosar.model.element import Element


class AbstractValueSpecification(ArObject):
    def __init__(
            self,
            short_label: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.short_label = short_label


class AbstractRuleBasedValueSpecification(AbstractValueSpecification):
    """Abstract"""


@dataclass(repr=False)
class ApplicationRuleBasedValueSpecification(AbstractRuleBasedValueSpecification):
    category: str
    sw_axis_cont: list[object] = field(default_factory=list)  # TODO: Implement
    sw_value_cont: object | None = None  # TODO: Implement


@dataclass(repr=False)
class CompositeRuleBasedValueSpecification(AbstractRuleBasedValueSpecification):
    rule: str
    argument: object  # TODO: Implement
    compoundPrimitiveArgument: list[object] = field(default_factory=list)  # TODO: Implement
    maxSizeToFill: int | None = None


@dataclass(repr=False)
class NumericalRuleBasedValueSpecification(AbstractRuleBasedValueSpecification):
    rule_based_values: object  # TODO: Implement


@dataclass(repr=False)
class ApplicationValueSpecification(AbstractValueSpecification):
    category: str
    sw_axis_cont: list[object] = field(default_factory=list)  # TODO: Implement
    sw_value_cont: object | None = None  # TODO: Implement


class CompositeValueSpecification(AbstractValueSpecification):
    """Abstract"""


@dataclass(repr=False)
class ArrayValueSpecification(CompositeValueSpecification):
    elements: list['ValueSpecification'] = field(default_factory=list)  # type: ignore
    intended_partial_initialization_count: int | None = None


@dataclass(repr=False)
class RecordValueSpecification(CompositeValueSpecification):
    fields: list['ValueSpecification'] = field(default_factory=list)  # type: ignore


@dataclass(repr=False)
class ConstantReference(AbstractValueSpecification):
    constant_ref: str


@dataclass(repr=False)
class NotAvailableValueSpecification(AbstractValueSpecification):
    default_pattern: int | None = None


@dataclass(repr=False)
class NumericalValueSpecification(AbstractValueSpecification):
    value: int | float


@dataclass(repr=False)
class ReferenceValueSpecification(AbstractValueSpecification):
    reference_value_ref: str


@dataclass(repr=False)
class TextValueSpecification(AbstractValueSpecification):
    value: str


ValueSpecification = TypeVar('ValueSpecification', bound=AbstractValueSpecification)
RuleBasedValueSpecification = TypeVar('RuleBasedValueSpecification', bound=AbstractRuleBasedValueSpecification)
AnyCompositeValueSpecification = TypeVar('AnyCompositeValueSpecification', bound=CompositeValueSpecification)


class ConstantSpecification(Element):
    def __init__(
            self,
            value_spec: ValueSpecification,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.value_spec = value_spec
