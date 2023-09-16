from autosar.ar_object import ArObject
from autosar.element import Element


class SwcImplementation(Element):
    """ Swc implementation """

    def __init__(self, name: str, behavior_ref: str, parent: ArObject | None = None):
        super().__init__(name, parent)
        self.behavior_ref = behavior_ref
        self.code_descriptors: list[SwcImplementationCodeDescriptor] | None = None
        self.programming_language: str | None = None
        self.resource_consumption: list[ResourceConsumption] | None = None
        self.sw_version: str | None = None
        self.use_code_generator: str | None = None
        self.vendor_id: str | None = None


class SwcImplementationCodeDescriptor(Element):
    """ Swc implementation code """

    def __init__(self, name: str, parent: ArObject | None = None):
        super().__init__(name, parent)
        # Autosar 4
        self.artifact_descriptors: list[EngineeringObject] | None = None
        # Autosar 3
        self.type: str | None = None


class EngineeringObject(ArObject):
    """ EngineeringObject """

    def __init__(self, parent: ArObject | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.short_label: str | None = None
        self.category: str | None = None
        self.revision_labels: list[str] | None = None
        self.domain: str | None = None


class ResourceConsumption(Element):
    """ Swc implementation ResourceConsumption """

    def __init__(self, name: str, parent: ArObject | None = None):
        super().__init__(name, parent)
        self.memory_sections: list[MemorySection] | None = None


class MemorySection(Element):
    """ Swc implementation MemorySection """

    def __init__(self, name: str, parent: ArObject | None = None):
        super().__init__(name, parent)
        self.alignment: str | None = None
        self.mem_class_symbol: str | None = None
        self.options: list[str] | None = None
        self.size: int | None = None
        self.sw_addr_method_ref: str | None = None
        self.symbol: str | None = None
