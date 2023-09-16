"""
Implements the class SwcImplementationParser
"""
from xml.etree.ElementTree import Element

from autosar.ar_object import ArObject
from autosar.component import SwcImplementation
from autosar.parser.parser_base import ElementParser
from autosar.swc_implementation import SwcImplementationCodeDescriptor, EngineeringObject, ResourceConsumption, MemorySection


class SwcImplementationParser(ElementParser):
    """
    ComponentType parser
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_tag = 'SWC-IMPLEMENTATION'

    def get_supported_tags(self):
        return [self.class_tag]

    def parse_element(self, xml_element: Element, parent: ArObject | None = None) -> SwcImplementation:
        """
        parser for the class.
        """
        assert (xml_element.tag == 'SWC-IMPLEMENTATION')
        ws = parent.root_ws()
        assert (ws is not None)
        name = self.parse_text_node(xml_element.find('SHORT-NAME'))
        behavior_ref = self.parse_text_node(xml_element.find('BEHAVIOR-REF'))
        implementation = SwcImplementation(name, behavior_ref, parent=parent)
        self.push()
        for xml_elem in xml_element.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                continue
            elif xml_elem.tag == 'BEHAVIOR-REF':
                continue
            elif xml_elem.tag == 'BUILD-ACTION-MANIFESTS':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'CODE-DESCRIPTORS':
                # Create the list to indicate that the base element exists.
                implementation.code_descriptors = []
                for code_elem in xml_elem.findall('./*'):
                    if code_elem.tag != 'CODE':
                        self._logger.error(f'Unexpected tag: {code_elem.tag}')
                        continue
                    implementation.code_descriptors.append(self.parse_code_descriptor(code_elem, parent=implementation))
            elif xml_elem.tag == 'COMPILERS':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'GENERATED-ARTIFACTS':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'HW-ELEMENT-REFS':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'LINKERS':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'MC-SUPPORT':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'PROGRAMMING-LANGUAGE':
                implementation.programming_language = self.parse_text_node(xml_elem)
                continue
            elif xml_elem.tag == 'REQUIRED-ARTIFACTS':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'REQUIRED-GENERATOR-TOOLS':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'RESOURCE-CONSUMPTION':
                implementation.resource_consumption = self.parse_resource_consumption(xml_elem, parent=implementation)
            elif xml_elem.tag == 'SW-VERSION':
                implementation.sw_version = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'SWC-BSW-MAPPING-REF':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'USED-CODE-GENERATOR':
                implementation.use_code_generator = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'VENDOR-ID':
                implementation.vendor_id = self.parse_int_node(xml_elem)
            else:
                self.default_handler(xml_elem)
        self.pop(implementation)
        # Find the SWC and connect the swc to the implementation.
        behavior = ws.find(behavior_ref)
        if behavior is not None:
            swc = ws.find(behavior.component_ref)
            if swc is not None:
                swc.implementation = implementation
        return implementation

    def parse_code_descriptor(self, xml_element: Element, parent: ArObject | None = None) -> SwcImplementationCodeDescriptor:
        """
        Parser for implementation code descriptor.
        """
        assert (xml_element.tag == 'CODE')
        name = self.parse_text_node(xml_element.find('SHORT-NAME'))
        code = SwcImplementationCodeDescriptor(name, parent=parent)
        self.push()
        for xml_elem in xml_element.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                continue
            elif xml_elem.tag == 'ARTIFACT-DESCRIPTORS':
                code.artifact_descriptors = []
                for desc_elem in xml_elem.findall('./*'):
                    if desc_elem.tag == 'AUTOSAR-ENGINEERING-OBJECT':
                        engineering_object = EngineeringObject(code)
                        for elem in desc_elem.findall('./*'):
                            if elem.tag == 'SHORT-LABEL':
                                engineering_object.short_label = self.parse_text_node(elem)
                            elif elem.tag == 'CATEGORY':
                                engineering_object.category = self.parse_text_node(elem)
                            elif elem.tag == 'REVISION-LABELS':
                                engineering_object.revision_labels = []
                                for label_elem in elem.findall('./*'):
                                    if label_elem.tag == 'REVISION-LABEL':
                                        engineering_object.revision_labels.append(self.parse_text_node(label_elem))
                            elif elem.tag == 'DOMAIN':
                                engineering_object.domain = self.parse_text_node(elem)
                        code.artifact_descriptors.append(engineering_object)
            elif xml_elem.tag == 'CALLBACK-HEADER-REFS':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'TYPE':
                # Only valid in Autosar 3.
                code.type = self.parse_text_node(xml_elem)
            else:
                self.default_handler(xml_elem)
        self.pop(code)
        return code

    def parse_resource_consumption(self, xml_element: Element, parent: ArObject | None = None) -> ResourceConsumption:
        """
        Parser for implementation resource consumption.
        """
        assert (xml_element.tag == 'RESOURCE-CONSUMPTION')
        name = self.parse_text_node(xml_element.find('SHORT-NAME'))
        res = ResourceConsumption(name, parent=parent)
        self.push()
        for xml_elem in xml_element.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                continue
            elif xml_elem.tag == 'EXECUTION-TIMES':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'HEAP-USAGES':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'MEMORY-SECTIONS':
                res.memory_sections = []
                for xml_section in xml_elem.findall('./*'):
                    res.memory_sections.append(self.parse_memory_section(xml_section, res))
            elif xml_elem.tag == 'SECTION-NAME-PREFIXS':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'STACK-USAGES':
                # TODO: Implement later
                continue
            else:
                self.default_handler(xml_elem)
        self.pop(res)
        return res

    def parse_memory_section(self, xml_element: Element, parent: ArObject | None = None) -> MemorySection:
        """
        Parser for memory section.
        """
        assert (xml_element.tag == 'MEMORY-SECTION')
        name = self.parse_text_node(xml_element.find('SHORT-NAME'))
        section = MemorySection(name, parent=parent)
        self.push()
        for xml_elem in xml_element.findall('./*'):
            if xml_elem.tag == 'SHORT-NAME':
                continue
            elif xml_elem.tag == 'ALIGNMENT':
                section.alignment = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'EXECUTABLE-ENTITY-REFS':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'MEM-CLASS-SYMBOL':
                section.mem_class_symbol = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'OPTIONS':
                section.options = []
                for xml_option in xml_elem.findall('./*'):
                    section.options.append(self.parse_text_node(xml_option))
            elif xml_elem.tag == 'PREFIX-REF':
                # TODO: Implement later
                continue
            elif xml_elem.tag == 'SIZE':
                section.size = self.parse_int_node(xml_elem)
            elif xml_elem.tag == 'SW-ADDRMETHOD-REF':
                section.sw_addr_method_ref = self.parse_text_node(xml_elem)
            elif xml_elem.tag == 'SYMBOL':
                section.symbol = self.parse_text_node(xml_elem)
            else:
                self.default_handler(xml_elem)
        self.pop(section)
        return section
