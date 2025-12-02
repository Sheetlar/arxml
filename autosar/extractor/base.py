class SystemElement:
    _instances: dict[str, 'SystemElement'] = {}

    def __new__(cls, identifier: str, *args, **kwargs):
        if (inst := cls._instances.get(identifier, None)) is not None:
            return inst
        inst = object.__new__(cls)
        cls._instances[identifier] = inst
        return inst

    def __init__(
            self,
            identifier: str,
            name: str,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._identifier = identifier
        self.name = name

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    @classmethod
    def get(cls, identifier: str) -> 'SystemElement':
        return cls._instances[identifier]
