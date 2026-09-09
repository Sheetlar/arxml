from autosar.extractor.system.module_ecu import EcuExtractionModule
from autosar.extractor.system.module_pdu import PduExtractionModule
from autosar.extractor.system.module_signal import SignalExtractionModule
from autosar.extractor.system.module_topology import TopologyExtractionModule
from autosar.model.ar_object import AnyArObject
from autosar.model.system import System


class ExtractedSystem(EcuExtractionModule, SignalExtractionModule, PduExtractionModule, TopologyExtractionModule):
    def __init__(
            self,
            ar_system: System,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.ar_system = ar_system
        self._get_fibex_elements_map()
        self._extract_ecus()
        self._build_signals()
        # self._build_signal_groups()
        self._extract_pdus()
        self._extract_topology()

    def _find(self, ref: str) -> AnyArObject | None:
        return self.ar_system.find(ref)

    def _get_fibex_elements_map(self):
        for fe_ref in self.ar_system.fibex_element_refs:
            if (elem := self._find(fe_ref)) is None:
                self._logger.warning(f'Cannot find fibex element {fe_ref}')
                continue
            if type(elem) not in self.fibex_elements:
                self.fibex_elements[type(elem)] = []
            self.fibex_elements[type(elem)].append(elem)
