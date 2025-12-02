from dataclasses import dataclass
from typing import TypeVar

from autosar import ArObject
from autosar.model.base import Limit


class CompuConstContent(ArObject):
    pass


@dataclass
class CompuConstFormulaContent(CompuConstContent):
    vfs: list[int | float]


@dataclass
class CompuConstNumericContent(CompuConstContent):
    v: int | float | None = None


@dataclass
class CompuConstTextContent(CompuConstContent):
    vt: str | None = None


AnyCompuConstContent = TypeVar('AnyCompuConstContent', bound=CompuConstContent)


@dataclass
class CompuConst(ArObject):
    compu_const_content_type: AnyCompuConstContent | None = None


@dataclass
class CompuNumeratorDenominator(ArObject):
    vs: list[int | float] | None = None


@dataclass
class CompuRationalCoeffs(ArObject):
    compu_numerator: CompuNumeratorDenominator | None = None
    compu_denominator: CompuNumeratorDenominator | None = None


class CompuScaleContents(ArObject):
    pass


@dataclass
class CompuScaleConstantContents(CompuScaleContents):
    compu_const: CompuConst | None = None


@dataclass
class CompuScaleRationalFormula(CompuScaleContents):
    compu_rational_coeffs: CompuRationalCoeffs | None = None


AnyCompuScaleContents = TypeVar('AnyCompuScaleContents', bound=CompuScaleContents)


class CompuScale(ArObject):
    def __init__(
            self,
            lower_limit: Limit | None = None,
            upper_limit: Limit | None = None,
            short_label: str | None = None,
            symbol: str | None = None,
            mask: int | None = None,
            desc: str | None = None,
            compu_inverse_value: CompuConst | None = None,
            compu_scale_contents: AnyCompuScaleContents | None = None,
            a2l_display_text: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.short_label = short_label
        self.symbol = symbol
        self.mask = mask
        self.desc = desc
        self.compu_inverse_value = compu_inverse_value
        self.compu_scale_contents = compu_scale_contents
        self.a2l_display_text = a2l_display_text

    @property
    def text_value(self) -> str | None:
        if not isinstance(self.compu_scale_contents, CompuScaleConstantContents):
            return None
        const = self.compu_scale_contents.compu_const
        if not isinstance(const.compu_const_content_type, CompuConstTextContent):
            return None
        return const.compu_const_content_type.vt

    @property
    def offset(self) -> int | float:
        self._check_rational_formula()
        numerator = self.compu_scale_contents.compu_rational_coeffs.compu_numerator
        if len(numerator.vs) == 0:
            return 0
        return numerator.vs[0]

    @property
    def numerator(self) -> int | float:
        self._check_rational_formula()
        numerator = self.compu_scale_contents.compu_rational_coeffs.compu_numerator
        if len(numerator.vs) < 2:
            return 0
        return numerator.vs[1]

    @property
    def denominator(self) -> int | float:
        self._check_rational_formula()
        denominator = self.compu_scale_contents.compu_rational_coeffs.compu_denominator
        if len(denominator.vs) == 0:
            return 1
        return denominator.vs[0]

    def _check_rational_formula(self):
        if not isinstance(self.compu_scale_contents, CompuScaleRationalFormula):
            raise TypeError('Compu contents must be CompuScaleRationalFormula')
        if self.compu_scale_contents.compu_rational_coeffs is None:
            raise TypeError('Coefficients of the rational function not provided')
