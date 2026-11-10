from xml.etree.ElementTree import Element

from autosar.model.communication.secure_comm import (
    SecureCommunicationAuthenticationProps,
    SecureCommunicationFreshnessProps,
    SecureCommunicationPropsSet,
    CryptoServicePrimitive,
    CryptoServiceKey,
    CryptoServiceQueue,
)
from autosar.model.enums import CryptoServiceKeyGenerationEnum
from autosar.model.value_spec import ValueSpecification
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    handler,
    multiple_with_check,
    single_subclass_aggr,
)
from autosar.parser.value_spec_parser import ValueSpecificationParserSelector


class SecureCommunicationAuthenticationPropsParser(
    IdentifiableParser[SecureCommunicationAuthenticationProps]
):
    _returned_type = SecureCommunicationAuthenticationProps

    @handler('AUTH-INFO-TX-LENGTH')
    def _parse_auth_info_tx_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)


class SecureCommunicationFreshnessPropsParser(
    IdentifiableParser[SecureCommunicationFreshnessProps]
):
    _returned_type = SecureCommunicationFreshnessProps

    @handler('FRESHNESS-COUNTER-SYNC-ATTEMPTS')
    def _parse_freshness_counter_sync_attempts(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('FRESHNESS-TIMESTAMP-TIME-PERIOD-FACTOR')
    def _parse_freshness_timestamp_time_period_factor(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('FRESHNESS-VALUE-LENGTH')
    def _parse_freshness_value_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('FRESHNESS-VALUE-TX-LENGTH')
    def _parse_freshness_value_tx_length(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('USE_FRESHNESS_TIMESTAMP')
    def _parse_use_freshness_timestamp(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)


class SecureCommunicationPropsSetParser(
    IdentifiableParser[SecureCommunicationPropsSet]
):
    _returned_type = SecureCommunicationPropsSet

    @handler('AUTHENTICATION-PROPSS', param='authentication_props')
    @multiple_with_check(expected_name='SECURE-COMMUNICATION-AUTHENTICATION-PROPS')
    def _parse_(self, xml_element: Element) -> SecureCommunicationAuthenticationProps | None:
        parser = SecureCommunicationAuthenticationPropsParser()
        return parser.parse_element(xml_element)

    @handler('FRESHNESS-PROPSS', param='freshness_props')
    @multiple_with_check(expected_name='SECURE-COMMUNICATION-FRESHNESS-PROPS')
    def _parse_(self, xml_element: Element) -> SecureCommunicationFreshnessProps | None:
        parser = SecureCommunicationFreshnessPropsParser()
        return parser.parse_element(xml_element)


class CryptoServicePrimitiveParser(IdentifiableParser[CryptoServicePrimitive]):
    _returned_type = CryptoServicePrimitive

    @handler('ALGORITHM-FAMILY')
    def _parse_algorithm_family(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ALGORITHM-SECONDARY-FAMILY')
    def _parse_algorithm_secondary_family(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ALGORITHM-MODE')
    def _parse_algorithm_mode(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class CryptoServiceKeyParser(IdentifiableParser[CryptoServiceKey]):
    _returned_type = CryptoServiceKey

    @handler('LENGTH', required=True)
    def _parse_length(self, xml_element: Element) -> int:
        if (length := self._parse_int_node(xml_element)) is None:
            raise ValueError
        return length

    @handler('ALGORITHM-FAMILY')
    def _parse_algorithm_family(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('DEVELOPMENT-VALUE')
    @single_subclass_aggr
    def _parse_development_value(self, xml_element: Element) -> ValueSpecification | None:
        parser = ValueSpecificationParserSelector(xml_element.tag)
        return parser.parse_element(xml_element)

    @handler('KEY-GENERATION')
    def _parse_key_generation(self, xml_element: Element) -> CryptoServiceKeyGenerationEnum | None:
        return self._parse_enum_node(xml_element, CryptoServiceKeyGenerationEnum)

    @handler('KEY-STORAGE-TYPE')
    def _parse_key_storage_type(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class CryptoServiceQueueParser(IdentifiableParser[CryptoServiceQueue]):
    _returned_type = CryptoServiceQueue

    @handler('QUEUE-SIZE')
    def _parse_queue_size(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)
