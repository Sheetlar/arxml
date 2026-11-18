from typing import TypeVar, Iterable

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


class ApplicationRuleBasedValueSpecification(AbstractRuleBasedValueSpecification):
    def __init__(
            self,
            category: str,
            sw_axis_cont: Iterable[object] | None = None,  # TODO: Implement
            sw_value_cont: object | None = None,  # TODO: Implement
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.category = category
        self.sw_axis_cont = self.eval_children(sw_axis_cont)
        self.sw_value_cont = sw_value_cont


class CompositeRuleBasedValueSpecification(AbstractRuleBasedValueSpecification):
    def __init__(
            self,
            rule: str,
            argument: object,  # TODO: Implement
            compound_primitive_argument: Iterable[object] | None = None,  # TODO: Implement
            max_size_to_fill: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.rule = rule
        self.argument = argument
        self.compound_primitive_argument = self.eval_children(compound_primitive_argument)
        self.max_size_to_fill = max_size_to_fill


class NumericalRuleBasedValueSpecification(AbstractRuleBasedValueSpecification):
    def __init__(
            self,
            rule_based_values: object,  # TODO: Implement
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.rule_based_values = rule_based_values


class ApplicationValueSpecification(AbstractValueSpecification):
    def __init__(
            self,
            category: str,
            sw_axis_cont: Iterable[object] | None = None,  # TODO: Implement
            sw_value_cont: object | None = None,  # TODO: Implement
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.category = category
        self.sw_axis_cont = self.eval_children(sw_axis_cont)
        self.sw_value_cont = sw_value_cont


class CompositeValueSpecification(AbstractValueSpecification):
    """Abstract"""


class ArrayValueSpecification(CompositeValueSpecification):
    def __init__(
            self,
            elements: Iterable['ValueSpecification'] | None = None,  # type: ignore
            intended_partial_initialization_count: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.elements = self.eval_children(elements)
        self.intended_partial_initialization_count = intended_partial_initialization_count


class RecordValueSpecification(CompositeValueSpecification):
    def __init__(
            self,
            fields: Iterable['ValueSpecification'] | None = None,  # type: ignore
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.fields = self.eval_children(fields)


class ConstantReference(AbstractValueSpecification):
    def __init__(
            self,
            constant_ref: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.constant_ref = constant_ref


class NotAvailableValueSpecification(AbstractValueSpecification):
    def __init__(
            self,
            default_pattern: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.default_pattern = default_pattern


class NumericalValueSpecification(AbstractValueSpecification):
    def __init__(
            self,
            value: int | float,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.value = value


class ReferenceValueSpecification(AbstractValueSpecification):
    def __init__(
            self,
            reference_value_ref: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.reference_value_ref = reference_value_ref


class TextValueSpecification(AbstractValueSpecification):
    def __init__(
            self,
            value: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.value = value


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
