from typing import TypeVar, Any, Sequence
from xml.etree.ElementTree import Element

from autosar.misc import not_none
from autosar.model.instance_ref import (
    AtpInstanceRef,
    AnyInstanceRef,
    ComponentInSystemInstanceRef,
    DataPrototypeInSystemInstanceRef,
    DataPrototypeInClientServerInterfaceInstanceRef,
    DataPrototypeInSenderReceiverInterfaceInstanceRef,
    OperationInSystemInstanceRef,
    VariableDataPrototypeInSystemInstanceRef,
    PortGroupInSystemInstanceRef,
    TriggerInSystemInstanceRef,
)
from autosar.parser.parser_base import handler, skip_return, BasicParser

IR = TypeVar('IR', bound=AtpInstanceRef)


class InstanceRefParser(BasicParser[IR]):
    _context_refs_param_name: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context_refs: list[str] = []

    def _scan_element(self, xml_element: Element) -> dict[str, Any] | None:
        kwargs = super()._scan_element(xml_element)
        if kwargs is not None:
            kwargs[self._context_refs_param_name] = self._context_refs
        return kwargs


class InstanceRefParserMulti(BasicParser[IR]):
    _context_refs_param_name: Sequence[str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context_refs: dict[str, list[str]] = {n: [] for n in self._context_refs_param_name}

    def _scan_element(self, xml_element: Element) -> dict[str, Any] | None:
        kwargs = super()._scan_element(xml_element)
        if kwargs is not None:
            kwargs.update(self._context_refs)
        return kwargs


class AnyInstRefParser(InstanceRefParser[AnyInstanceRef]):
    _returned_type = AnyInstanceRef
    _context_refs_param_name = 'context_element_refs'

    @handler('BASE-REF')
    def _parse_base(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-ELEMENT-REF')
    @skip_return
    def _parse_context_element_single(self, xml_element: Element):
        if (ref := self._parse_text_node(xml_element)) is not None:
            self._context_refs.append(ref)

    @handler('CONTEXT-ELEMENT-REFS')
    @skip_return
    def _parse_context_element_multiple(self, xml_element: Element):
        children = xml_element.findall('CONTEXT-ELEMENT-REF')
        self._context_refs.extend(filter(not_none, map(self._parse_text_node, children)))

    @handler('TARGET-REF')
    def _parse_target(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


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
    def _parse_target_component(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class DataPrototypeInSystemInstRefParser(InstanceRefParserMulti[DataPrototypeInSystemInstanceRef]):
    _returned_type = DataPrototypeInSystemInstanceRef
    _context_refs_param_name = (
        'context_component_refs',
        'context_data_prototype_refs',
    )

    @handler('BASE-REF')
    def _parse_base(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-ROOT-COMPOSITION-REF')
    def _parse_context_root_composition(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-COMPONENT-REF')
    @skip_return
    def _parse_context_component_single(self, xml_element: Element):
        if (ref := self._parse_text_node(xml_element)) is not None:
            self._context_refs['context_component_refs'].append(ref)

    @handler('CONTEXT-COMPONENT-REFS')
    @skip_return
    def _parse_context_component_multiple(self, xml_element: Element):
        children = xml_element.findall('CONTEXT-COMPONENT-REF')
        self._context_refs['context_component_refs'].extend(
            filter(not_none, map(self._parse_text_node, children))
        )

    @handler('CONTEXT-PORT-REF')
    def _parse_context_port(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ROOT-DATA-PROTOTYPE-REF')
    def _parse_root_data_prototype(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-DATA-PROTOTYPE-REF')
    @skip_return
    def _parse_context_component_single(self, xml_element: Element):
        if (ref := self._parse_text_node(xml_element)) is not None:
            self._context_refs['context_data_prototype_refs'].append(ref)

    @handler('CONTEXT-DATA-PROTOTYPE-REFS')
    @skip_return
    def _parse_context_component_multiple(self, xml_element: Element):
        children = xml_element.findall('CONTEXT-DATA-PROTOTYPE-REF')
        self._context_refs['context_data_prototype_refs'].extend(
            filter(not_none, map(self._parse_text_node, children))
        )

    @handler('TARGET-DATA-PROTOTYPE-REF')
    def _parse_target_data_prototype(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class DataPrototypeInClientServerInterfaceInstRefParser(
    InstanceRefParser[DataPrototypeInClientServerInterfaceInstanceRef]
):
    _returned_type = DataPrototypeInClientServerInterfaceInstanceRef
    _context_refs_param_name = 'context_data_prototype_in_cs_refs'

    @handler('BASE-REF')
    def _parse_base(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ROOT-DATA-PROTOTYPE-IN-CS-REF')
    def _parse_root_data_prototype(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-DATA-PROTOTYPE-IN-CS-REF')
    @skip_return
    def _parse_context_component_single(self, xml_element: Element):
        if (ref := self._parse_text_node(xml_element)) is not None:
            self._context_refs.append(ref)

    @handler('CONTEXT-DATA-PROTOTYPE-IN-CS-REFS')
    @skip_return
    def _parse_context_component_multiple(self, xml_element: Element):
        children = xml_element.findall('CONTEXT-DATA-PROTOTYPE-IN-CS-REF')
        self._context_refs.extend(
            filter(not_none, map(self._parse_text_node, children))
        )

    @handler('TARGET-DATA-PROTOTYPE-IN-CS-REF')
    def _parse_target_data_prototype(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class DataPrototypeInSenderReceiverInterfaceInstRefParser(
    InstanceRefParser[DataPrototypeInSenderReceiverInterfaceInstanceRef]
):
    _returned_type = DataPrototypeInSenderReceiverInterfaceInstanceRef
    _context_refs_param_name = 'context_data_prototype_in_sr_refs'

    @handler('BASE-REF')
    def _parse_base(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ROOT-DATA-PROTOTYPE-IN-SR-REF')
    def _parse_root_data_prototype(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CONTEXT-DATA-PROTOTYPE-IN-SR-REF')
    @skip_return
    def _parse_context_component_single(self, xml_element: Element):
        if (ref := self._parse_text_node(xml_element)) is not None:
            self._context_refs.append(ref)

    @handler('CONTEXT-DATA-PROTOTYPE-IN-SR-REFS')
    @skip_return
    def _parse_context_component_multiple(self, xml_element: Element):
        children = xml_element.findall('CONTEXT-DATA-PROTOTYPE-IN-SR-REF')
        self._context_refs.extend(
            filter(not_none, map(self._parse_text_node, children))
        )

    @handler('TARGET-DATA-PROTOTYPE-IN-SR-REF')
    def _parse_target_data_prototype(self, xml_element: Element) -> str | None:
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


class PortGroupInSystemInstRefParser(InstanceRefParser[PortGroupInSystemInstanceRef]):
    _returned_type = PortGroupInSystemInstanceRef
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

    @handler('TARGET-REF')
    def _parse_target(self, xml_element: Element) -> str | None:
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
