from abc import ABC

from autosar.extractor.system.extractor_base import AbstractExtractor, ArxmlExtractionError
from autosar.extractor.topology import Ecu
from autosar.model.ecu import EcuInstance


class EcuExtractionModule(AbstractExtractor, ABC):
    def _extract_ecus(self):
        try:
            self.ecus = tuple(
                Ecu(identifier=ecu.ref, name=ecu.name)
                for ecu in self.fibex_elements[EcuInstance]
            )
        except KeyError:
            raise ArxmlExtractionError('No ECU instances found')
