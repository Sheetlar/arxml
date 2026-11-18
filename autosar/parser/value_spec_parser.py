from xml.etree.ElementTree import Element

from autosar.model.value_spec import (
    ArrayValueSpecification,
    RecordValueSpecification,
    ConstantReference,
    NotAvailableValueSpecification,
    NumericalValueSpecification,
    ReferenceValueSpecification,
    TextValueSpecification,
    ValueSpecification,
    ConstantSpecification,
)
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    multiple,
    single_subclass_aggr,
    BasicParser,
    ParserSelector,
)


class ValueSpecificationParser(BasicParser[ValueSpecification]):
    @handler('SHORT-LABEL')
    def _parse_short_label(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class ArrayValueSpecificationParser(ValueSpecificationParser[ArrayValueSpecification]):
    _returned_type = ArrayValueSpecification

    @handler('ELEMENTS')
    @multiple
    def _parse_element(self, xml_element: Element) -> ValueSpecification | None:
        parser = ValueSpecificationParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('INTENDED-PARTIAL-INITIALIZATION-COUNT')
    def _parse_intended_partial_initialization_count(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class RecordValueSpecificationParser(ValueSpecificationParser[RecordValueSpecification]):
    _returned_type = RecordValueSpecification

    @handler('FIELDS')
    @multiple
    def _parse_field(self, xml_element: Element) -> ValueSpecification | None:
        parser = ValueSpecificationParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)


class ConstantReferenceParser(ValueSpecificationParser[ConstantReference]):
    _returned_type = ConstantReference

    @handler('CONSTANT-REF', required=True)
    def _parse_constant(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref


class NotAvailableValueSpecificationParser(ValueSpecificationParser[NotAvailableValueSpecification]):
    _returned_type = NotAvailableValueSpecification

    @handler('DEFAULT-PATTERN')
    def _parse_default_pattern(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class NumericalValueSpecificationParser(ValueSpecificationParser[NumericalValueSpecification]):
    _returned_type = NumericalValueSpecification

    @handler('VALUE', required=True)
    def _parse_value(self, xml_element: Element) -> int | float:
        if (value := self._parse_number_node(xml_element)) is None:
            raise ValueError
        return value


class ReferenceValueSpecificationParser(ValueSpecificationParser[ReferenceValueSpecification]):
    _returned_type = ReferenceValueSpecification

    @handler('REFERENCE-VALUE-REF', required=True)
    def _parse_reference_value(self, xml_element: Element) -> str:
        if (ref := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return ref


class TextValueSpecificationParser(ValueSpecificationParser[TextValueSpecification]):
    _returned_type = TextValueSpecification

    @handler('VALUE', required=True)
    def _parse_value(self, xml_element: Element) -> str:
        if (value := self._parse_text_node(xml_element)) is None:
            raise ValueError
        return value


class ValueSpecificationParserSelector(ParserSelector[ValueSpecification]):
    _tag_map = {
        'ARRAY-VALUE-SPECIFICATION': ArrayValueSpecificationParser,
        'RECORD-VALUE-SPECIFICATION': RecordValueSpecificationParser,
        'CONSTANT-REFERENCE': ConstantReferenceParser,
        'NOT-AVAILABLE-VALUE-SPECIFICATION': NotAvailableValueSpecificationParser,
        'NUMERICAL-VALUE-SPECIFICATION': NumericalValueSpecificationParser,
        'REFERENCE-VALUE-SPECIFICATION': ReferenceValueSpecificationParser,
        'TEXT-VALUE-SPECIFICATION': TextValueSpecificationParser,
    }
    _not_implemented = {
        'APPLICATION-RULE-BASED-VALUE-SPECIFICATION',
        'COMPOSITE-RULE-BASED-VALUE-SPECIFICATION',
        'NUMERICAL-RULE-BASED-VALUE-SPECIFICATION',
        'APPLICATION-VALUE-SPECIFICATION',
    }


class ConstantSpecificationParser(IdentifiableParser[ConstantSpecification]):
    _returned_type = ConstantSpecification

    @handler('VALUE-SPEC')
    @single_subclass_aggr
    def _parse_value_spec(self, xml_element: Element) -> ValueSpecification | None:
        parser = ValueSpecificationParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)
