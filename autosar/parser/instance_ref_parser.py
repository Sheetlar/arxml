from typing import TypeVar, Any
from xml.etree.ElementTree import Element

from autosar.misc import not_none
from autosar.model.system import (
    AtpInstanceRef,
    ComponentInSystemInstanceRef,
    OperationInSystemInstanceRef,
    VariableDataPrototypeInSystemInstanceRef,
    TriggerInSystemInstanceRef,
)
from autosar.parser.parser_base import BasicParserWithoutParent, handler, skip_return

IR = TypeVar('IR', bound=AtpInstanceRef)


class InstanceRefParser(BasicParserWithoutParent[IR]):
    _context_refs_param_name: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context_refs: list[str] = []

    def _scan_element(self, xml_element: Element) -> dict[str, Any] | None:
        kwargs = super()._scan_element(xml_element)
        if kwargs is None:
            return None
        kwargs[self._context_refs_param_name] = self._context_refs
        return kwargs


class ComponentInSystemInstRefParser(InstanceRefParser[ComponentInSystemInstanceRef]):
    _returned_type = ComponentInSystemInstanceRef
    _context_refs_param_name = 'context_component_refs'

    @handler('BASE-REF')
    def _parse_base(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-COMPOSITION-REF')
    def _parse_context_composition(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-COMPONENT-REF')
    @skip_return
    def _parse_context_component_single(self, xml_element: Element):
        if (ref := self._parse_text_node(xml_element)) is not None:
            self._context_refs.append(ref)

    @handler('CONTEXT-COMPONENT-REFS')
    @skip_return
    def _parse_context_component_multiple(self, xml_element: Element):
        children = xml_element.findall('CONTEXT-COMPONENT-REF')
        self._context_refs.extend(filter(not_none, map(self._parse_text_node, children)))

    @handler('TARGET-COMPONENT-REF')
    def _parse_target_operation(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class OperationInSystemInstRefParser(InstanceRefParser[OperationInSystemInstanceRef]):
    _returned_type = OperationInSystemInstanceRef
    _context_refs_param_name = 'context_component_refs'

    @handler('BASE-REF')
    def _parse_base(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-COMPOSITION-REF')
    def _parse_context_composition(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-COMPONENT-REF')
    @skip_return
    def _parse_context_component_single(self, xml_element: Element):
        if (ref := self._parse_text_node(xml_element)) is not None:
            self._context_refs.append(ref)

    @handler('CONTEXT-COMPONENT-REFS')
    @skip_return
    def _parse_context_component_multiple(self, xml_element: Element):
        children = xml_element.findall('CONTEXT-COMPONENT-REF')
        self._context_refs.extend(filter(not_none, map(self._parse_text_node, children)))

    @handler('CONTEXT-PORT-REF')
    def _parse_context_port(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TARGET-OPERATION-REF')
    def _parse_target_operation(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class VariableDataPrototypeInSystemInstRefParser(InstanceRefParser[VariableDataPrototypeInSystemInstanceRef]):
    _returned_type = VariableDataPrototypeInSystemInstanceRef
    _context_refs_param_name = 'context_component_refs'

    @handler('BASE-REF')
    def _parse_base(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-COMPOSITION-REF')
    def _parse_context_composition(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-COMPONENT-REF')
    @skip_return
    def _parse_context_component_single(self, xml_element: Element):
        if (ref := self._parse_text_node(xml_element)) is not None:
            self._context_refs.append(ref)

    @handler('CONTEXT-COMPONENT-REFS')
    @skip_return
    def _parse_context_component_multiple(self, xml_element: Element):
        children = xml_element.findall('CONTEXT-COMPONENT-REF')
        self._context_refs.extend(filter(not_none, map(self._parse_text_node, children)))

    @handler('CONTEXT-PORT-REF')
    def _parse_context_port(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TARGET-DATA-PROTOTYPE-REF')
    def _parse_target_data_prototype(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class TriggerInSystemInstRefParser(InstanceRefParser[TriggerInSystemInstanceRef]):
    _returned_type = TriggerInSystemInstanceRef
    _context_refs_param_name = 'context_component_refs'

    @handler('BASE-REF')
    def _parse_base(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-COMPOSITION-REF')
    def _parse_context_composition(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-COMPONENT-REF')
    @skip_return
    def _parse_context_component_single(self, xml_element: Element):
        if (ref := self._parse_text_node(xml_element)) is not None:
            self._context_refs.append(ref)

    @handler('CONTEXT-COMPONENT-REFS')
    @skip_return
    def _parse_context_component_multiple(self, xml_element: Element):
        children = xml_element.findall('CONTEXT-COMPONENT-REF')
        self._context_refs.extend(filter(not_none, map(self._parse_text_node, children)))

    @handler('CONTEXT-PORT-REF')
    def _parse_context_port(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('TARGET-TRIGGER-REF')
    def _parse_target_trigger(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)
