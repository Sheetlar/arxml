from xml.etree.ElementTree import Element

from autosar.model.base import Limit
from autosar.model.compu import (
    CompuScale,
    CompuConst,
    CompuConstFormulaContent,
    CompuConstNumericContent,
    CompuConstTextContent,
    AnyCompuScaleContents,
    CompuScaleConstantContents,
    CompuScaleRationalFormula,
    CompuRationalCoeffs,
    CompuNumeratorDenominator,
)
from autosar.parser.parser_base import BaseParser


class CompuParser(BaseParser):
    compu_const_tag = 'COMPU-CONST'
    compu_rational_coeffs_tag = 'COMPU-RATIONAL-COEFFS'
    compu_scale_contents_tags = (
        compu_const_tag,
        compu_rational_coeffs_tag,
    )

    def parse_compu_scale(self, xml_elem: Element | None) -> CompuScale | None:
        if xml_elem is None:
            return None
        lower_limit: Limit | None = None
        upper_limit: Limit | None = None
        label: str | None = None
        symbol: str | None = None
        mask: int | None = None
        desc: str | None = None
        inverse: CompuConst | None = None
        a2l: str | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case tag if tag in self.compu_scale_contents_tags:
                    pass
                case 'LOWER-LIMIT':
                    lower_limit = self.parse_limit(child_elem)
                case 'UPPER-LIMIT':
                    upper_limit = self.parse_limit(child_elem)
                case 'SHORT-LABEL':
                    label = self.parse_text_node(child_elem)
                case 'SYMBOL':
                    symbol = self.parse_text_node(child_elem)
                case 'MASK':
                    mask = self.parse_int_node(child_elem)
                case 'DESC':
                    desc, _ = self.parse_desc_direct(child_elem)
                case 'COMPU-INVERSE-VALUE':
                    inverse = self.parse_compu_const(xml_elem)
                case 'A-2L-DISPLAY-TEXT':
                    a2l = self.parse_text_node(child_elem)
                case _:
                    self.log_unexpected(xml_elem, child_elem)
        contents = self._parse_compu_scale_contents(xml_elem)
        return CompuScale(
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            short_label=label,
            symbol=symbol,
            mask=mask,
            desc=desc,
            compu_inverse_value=inverse,
            compu_scale_contents=contents,
            a2l_display_text=a2l,
        )

    def parse_compu_const(self, xml_elem: Element, is_wrapped: bool = True) -> CompuConst:
        vfs: list[int | float] = []
        v: int | float | None = None
        vt: str | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case 'VF':
                    vfs.append(self.parse_number_node(child_elem))
                case 'V':
                    v = self.parse_number_node(child_elem)
                case 'VT':
                    vt = self.parse_text_node(child_elem)
                case _:
                    if is_wrapped:
                        self.log_unexpected(xml_elem, child_elem)
        if len(vfs) > 0:
            content = CompuConstFormulaContent(vfs=vfs)
        elif v is not None:
            content = CompuConstNumericContent(v=v)
        else:
            content = CompuConstTextContent(vt=vt)
        return CompuConst(compu_const_content_type=content)

    def _parse_compu_scale_contents(self, xml_elem: Element) -> AnyCompuScaleContents | None:
        const: CompuConst | None = None
        coeffs: CompuRationalCoeffs | None = None
        for child_elem in xml_elem:
            match child_elem.tag:
                case self.compu_const_tag:
                    const = self.parse_compu_const(child_elem)
                case self.compu_rational_coeffs_tag:
                    coeffs = self._parse_rational_coeffs(child_elem)
        if const is not None:
            return CompuScaleConstantContents(compu_const=const)
        if coeffs is not None:
            return CompuScaleRationalFormula(compu_rational_coeffs=coeffs)
        return None

    def _parse_rational_coeffs(self, xml_elem: Element) -> CompuRationalCoeffs:
        numerator = self._parse_numerator_denominator(xml_elem.find('COMPU-NUMERATOR'))
        denominator = self._parse_numerator_denominator(xml_elem.find('COMPU-DENOMINATOR'))
        return CompuRationalCoeffs(
            compu_numerator=numerator,
            compu_denominator=denominator,
        )

    def _parse_numerator_denominator(self, xml_elem: Element | None) -> CompuNumeratorDenominator | None:
        if xml_elem is None:
            return None
        factors = list(map(self.parse_number_node, xml_elem.findall('V')))
        return CompuNumeratorDenominator(vs=factors)
