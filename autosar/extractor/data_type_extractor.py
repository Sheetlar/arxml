from typing import Iterable

from autosar.data_transformation import TransformationTechnology, EndToEndTransformationDescription
from autosar.datatype import ApplicationDataType, ApplicationPrimitiveDataType, ApplicationRecordDataType, ApplicationArrayDataType, CompuMethod
from autosar.element import DataElement
from autosar.extractor.common import DataType, ScalableDataType, BitfieldDataType, EnumDataType, dtype_mapper, get_type_by_range, get_max_value
from autosar.extractor.e2e import e2e_profiles
from autosar.has_logger import HasLogger


class ExtractedDataType(HasLogger):
    def __init__(
            self,
            data_element: DataElement,
            transformations: Iterable[TransformationTechnology],
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._ws = data_element.root_ws()
        self._transformations = transformations
        self._logger.debug(f'Extracting {data_element.name}')
        self.root_type = self._ws.find(data_element.type_ref)
        self.elements = {}
        try:
            self._extract_e2e_transform()
            elements = self._recursive_element_extract(self.root_type)
            self.elements.update(elements)
        except NotImplementedError:
            self.elements = None

    def _extract_e2e_transform(self):
        for transform in self._transformations:
            if transform.protocol != 'E2E':
                continue
            description, = transform.transformation_descriptions
            if not isinstance(description, EndToEndTransformationDescription):
                continue
            profile = description.profile_name
            if profile not in e2e_profiles:
                raise NotImplementedError
            self.elements.update(e2e_profiles[profile])

    def _recursive_element_extract(
            self,
            element_type: ApplicationDataType,
            prefix: str = '',
    ) -> dict[str, ApplicationPrimitiveDataType]:
        if isinstance(element_type, ApplicationRecordDataType):
            result = {}
            for field in element_type.elements:
                field_element = self._ws.find(field.type_ref)
                field_result = self._recursive_element_extract(
                    field_element,
                    f'{prefix}{field.name}_',
                )
                result.update(field_result)
            return result
        if isinstance(element_type, ApplicationArrayDataType):
            element = self._ws.find(element_type.element.type_ref)
            if element_type.element.size_semantics != 'FIXED-SIZE':
                raise NotImplementedError
            result = self._recursive_element_extract(element)
            return {
                f'{prefix}{idx}_{n}': t
                for idx in range(element_type.element.array_size)
                for n, t in result.items()
            }
        if isinstance(element_type, ApplicationPrimitiveDataType):
            name = prefix.removesuffix('_')
            return {name: self._get_data_type(element_type)}
        raise NotImplementedError

    def _get_data_type(self, element_type: ApplicationPrimitiveDataType) -> DataType:
        compu_method: CompuMethod = self._ws.find(element_type.compu_method_ref)
        if compu_method is None:
            raise NotImplementedError
        name = compu_method.name
        unit_factor = 1
        if compu_method.unit_ref is not None:
            unit = self._ws.find(compu_method.unit_ref)
            unit_factor = unit.factor
            if isinstance(unit_factor, str):
                pass
        match compu_method.category:
            case 'IDENTICAL':
                dtype = dtype_mapper[name] if name in dtype_mapper else 'f'
                return ScalableDataType(name, dtype, 1 / unit_factor)
            case 'LINEAR':
                if compu_method.int_to_phys is None:
                    raise NotImplementedError
                dtype = get_type_by_range(
                    compu_method.int_to_phys.lower_limit,
                    compu_method.int_to_phys.upper_limit,
                )
                scale_element, = compu_method.int_to_phys.elements
                scale = scale_element.offset + scale_element.numerator / scale_element.denominator
                return ScalableDataType(name, dtype, scale / unit_factor)
            case 'TEXTTABLE':
                dtype = get_type_by_range(
                    compu_method.int_to_phys.lower_limit,
                    compu_method.int_to_phys.upper_limit,
                )
                mapping = {}
                for e in compu_method.int_to_phys.elements:
                    if e.lower_limit != e.upper_limit:
                        raise NotImplementedError
                    mapping[e.lower_limit] = e.label
                return EnumDataType(name, dtype, mapping)
            case 'BITFIELD_TEXTTABLE':
                values_off = {}
                values_on = {}
                for e in compu_method.int_to_phys.elements:
                    if e.lower_limit != e.upper_limit:
                        raise NotImplementedError
                    if e.lower_limit == 0:
                        values_off[e.mask] = e.text_value
                    values_on[e.mask] = e.lower_limit
                try:
                    desc = {m: (values_off[m], v) for m, v in values_on.items()}
                except KeyError:
                    raise NotImplementedError
                dtype = get_type_by_range(0, max(desc.keys()))
                return BitfieldDataType(name, dtype, desc)
            case 'SCALE_LINEAR_AND_TEXTTABLE':
                dtype = get_type_by_range(
                    compu_method.int_to_phys.lower_limit,
                    compu_method.int_to_phys.upper_limit,
                )
                scale_elem, = tuple(x for x in compu_method.int_to_phys.elements if x.text_value is None)
                if isinstance(scale_elem.upper_limit, float) and scale_elem.numerator == 1:
                    scale_elem.numerator = round(scale_elem.upper_limit / get_max_value(dtype), 5)
                scale = scale_elem.offset + scale_elem.numerator / scale_elem.denominator
                return ScalableDataType(name, dtype, scale / unit_factor)
            case _:
                raise NotImplementedError

    @staticmethod
    def check_size(element_len: int, array_size: int):
        return array_size * element_len <= 100000

    def __repr__(self):
        if self.elements is None:
            return f'{self.__class__.__name__}(NotImplemented)'
        return f'{self.__class__.__name__}(name={self.root_type.name!r}, elements_count={len(self.elements)})'
