from autosar.ar_object import ArObject
from autosar.base import AdminData
from autosar.element import (Element)


class ModeGroup(Element):
    """
    Implements <MODE-GROUP> (AUTOSAR4)
    Implements <MODE-DECLARATION-GROUP-PROTOTYPE> (AUTOSAR3)

    A ModeGroup inside a ModeSwitchInterface is what a DataElement is to a SenderReceiverInterface.
    """

    def __init__(
            self,
            name: str,
            type_ref: str,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.type_ref = type_ref

    @staticmethod
    def tag(version: int | float | None = None):
        if version is not None and version >= 4.0:
            return "MODE-GROUP"
        else:
            return "MODE-DECLARATION-GROUP-PROTOTYPE"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.name == other.name and self.admin_data == other.admin_data and self.type_ref == other.type_ref:
                return True
        return False

    def __ne__(self, other):
        return not (self == other)


class ModeDeclarationGroup(Element):
    """
    Implements <MODE-DECLARATION-GROUP> (AUTOSAR 4)

    Objects created from this class is expected to be placed inside a package with the role name "ModeDclrGroup".

    Attributes:
    modeDeclarations: A list of ModeDeclaration objects
    initialModeRef: Initial mode value

    """

    @staticmethod
    def tag(*_):
        return "MODE-DECLARATION-GROUP"

    def __init__(
            self,
            name: str,
            initial_mode_ref: str | None = None,
            mode_declarations: list['ModeDeclaration'] | None = None,
            category: str | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data, category)
        self.initial_mode_ref = initial_mode_ref
        if mode_declarations is None:
            mode_declarations = []
        self.mode_declarations: list[ModeDeclaration] = mode_declarations
        self.category = category

    def find(self, ref: str, *_):
        ref = ref.partition('/')
        name = ref[0]
        for elem in self.mode_declarations:
            if elem.name == name:
                return elem
        return None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.name == other.name and self.initial_mode_ref == other.initial_mode_ref and \
                    len(self.mode_declarations) == len(other.mode_declarations) and self.admin_data == other.admin_data:
                for i, left in enumerate(self.mode_declarations):
                    right = other.mode_declarations[i]
                    if left != right:
                        return False
                return True
        return False

    def __ne__(self, other):
        return not (self == other)


class ModeDeclaration(Element):
    """
    Implements <MODE-DECLARATION> (AUTOSAR4)
    """

    @staticmethod
    def tag(*_):
        return "MODE-DECLARATION"

    def __init__(
            self,
            name: str,
            value: int | None = None,
            parent: ArObject | None = None,
            admin_data: AdminData | None = None,
    ):
        super().__init__(name, parent, admin_data)
        self.value = int(value) if value is not None else None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.name == other.name:
                if self.value is None and other.value is None:
                    return True
                elif (self.value is not None) and (other.value is not None):
                    if self.value == other.value:
                        return True
        return False

    def __ne__(self, other):
        return not (self == other)
