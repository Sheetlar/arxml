from typing import Any
from xml.etree.ElementTree import Element

from autosar.misc import not_none
from autosar.model.admin_data import AdminData, SpecialDataGroup, SpecialData, NumericalSpecialData, MultiLanguagePlainText
from autosar.model.languages_enum import LEnum
from autosar.parser.parser_base import BasicParser, handler, not_implemented_handler, multiple_with_check, skip_return


class SpecialDataGroupParser(BasicParser[SpecialDataGroup]):
    _returned_type = SpecialDataGroup

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sdg_contents: list[SpecialData | NumericalSpecialData | SpecialDataGroup | str] = []

    def _parse_attributes(self, xml_element: Element) -> dict[str, Any]:
        try:
            return {'gid': xml_element.attrib['GID']}
        except KeyError:
            self._missing_required.add('GID')
            return {}

    def _scan_element(self, xml_element: Element) -> dict[str, Any] | None:
        kwargs = super()._scan_element(xml_element)
        if kwargs is None:
            return None
        kwargs['contents'] = self._sdg_contents
        return kwargs

    @handler('SD', 'SDF')
    @skip_return
    def _parse_sd(self, xml_element: Element):
        match xml_element.tag:
            case 'SD':
                cls = SpecialData
                value_parser = self._parse_text_node
            case 'SDF':
                cls = NumericalSpecialData
                value_parser = self._parse_number_node
            case _:
                return
        try:
            sd_gid = xml_element.attrib['GID']
        except KeyError:
            self._logger.error(f'Missing GID in {xml_element.tag}')
            return
        sd_value = value_parser(xml_element)
        if sd_value is None:
            self._logger.error(f'No value in {xml_element.tag}')
            return
        sd = cls(sd_gid, sd_value)  # type: ignore (typechecker FP)
        self._sdg_contents.append(sd)

    @handler('SDX')
    @skip_return
    def _parse_sdx(self, xml_element: Element):
        ref = self._parse_text_node(xml_element)
        if ref is None:
            return
        self._sdg_contents.append(ref)

    @not_implemented_handler('SDG-CAPTION')
    def _parse_caption(self, xml_element: Element):
        ...

    @handler('SDG')
    @skip_return
    def _parse_sdg(self, xml_element: Element):
        sdg_parser = SpecialDataGroupParser()
        if (sdg := sdg_parser.parse_element(xml_element)) is not None:
            self._sdg_contents.append(sdg)

    @not_implemented_handler('SDXFS', 'SDXF')
    def _parse_sdxf(self, xml_element: Element):
        ...


class AdminDataParser(BasicParser):
    _returned_type = AdminData

    @handler('SDGS')
    @multiple_with_check
    def _parse_sdg(self, xml_element: Element) -> SpecialDataGroup | None:
        sdg_parser = SpecialDataGroupParser()
        sdg = sdg_parser.parse_element(xml_element)
        return sdg

    @handler('LANGUAGE')
    def _parse_language(self, xml_element: Element) -> LEnum | None:
        return self._parse_enum_node(xml_element, LEnum)

    @handler('USED-LANGUAGES')
    def _parse_used_languages(self, xml_element: Element) -> MultiLanguagePlainText:
        def parse_l10(e: Element) -> tuple[LEnum, str] | None:
            try:
                lang = LEnum((e.attrib.get('L')))
            except ValueError:
                return None
            value = self._parse_text_node(e)
            if value is None:
                return None
            return lang, value

        return MultiLanguagePlainText(
            filter(not_none, map(parse_l10, xml_element.findall('L-10')))
        )

    @not_implemented_handler('DOC-REVISIONS')
    def _parse_doc_revision(self, xml_element: Element):
        ...
