from autosar.element import Element


class Collection(Element):
    def __init__(
            self,
            long_name: str | None = None,
            element_role: str | None = None,
            element_refs: list[str] | None = None,
            *args, **kwargs,
    ):
        if long_name is None:
            long_name = kwargs.get('name')
        super().__init__(*args, long_name=long_name, **kwargs)
        self.element_role = element_role
        if element_refs is None:
            element_refs = []
        self.element_refs = element_refs

        if element_role is not None:
            ws = self.root_ws()
            if element_role not in ws.role_elements:
                ws.role_elements[element_role] = []
            ws.role_elements[element_role].append(self)
