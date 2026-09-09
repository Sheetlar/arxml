from abc import ABC, abstractmethod

from autosar.misc import HasLogger
from autosar.model.ar_object import AnyArObject, MaybeArObject


class ArxmlExtractionError(Exception):
    pass


class AbstractExtractor(HasLogger, ABC):
    fibex_elements: dict[type[AnyArObject], list[AnyArObject]] = {}

    @abstractmethod
    def _find(self, ref: str) -> MaybeArObject:
        raise NotImplementedError
