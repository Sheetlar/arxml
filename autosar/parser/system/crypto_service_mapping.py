from typing import TypeVar
from xml.etree.ElementTree import Element

from autosar.model.enums import TlsVersionEnum
from autosar.model.system import (
    SecOcCryptoServiceMapping,
    TlsCryptoServiceMapping,
    TlsCryptoCipherSuite,
    TlsCryptoCipherSuiteProps,
    TlsPskIdentity,
)
from autosar.parser.identifiable import IdentifiableParser
from autosar.parser.parser_base import (
    ParserSelector,
    BasicParser,
    handler,
    multiple_with_check,
)

CSM = TypeVar('CSM', SecOcCryptoServiceMapping, TlsCryptoServiceMapping)


class TlsCryptoCipherSuitePropsParser(IdentifiableParser[TlsCryptoCipherSuiteProps]):
    _returned_type = TlsCryptoCipherSuiteProps

    @handler('TCP-IP-TLS-USE-SECURITY-EXTENSION-FORCE-ENCRYPT-THEN-MAC', param='use')
    def _parse_flag(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)


class TlsPskIdentityParser(BasicParser[TlsPskIdentity]):
    _returned_type = TlsPskIdentity

    @handler('PSK-IDENTITY')
    def _parse_psk_identity(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PSK-IDENTITY-HINT')
    def _parse_psk_identity_hint(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class TlsCryptoCipherSuiteParser(IdentifiableParser[TlsCryptoCipherSuite]):
    _returned_type = TlsCryptoCipherSuite

    @handler('AUTHENTICATION-REF')
    def _parse_authentication(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('AUTHENTICATION-KEY-REF')
    def _parse_authentication_key(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CIPHER-SUITE-ID')
    def _parse_cipher_suite_id(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('CIPHER-SUITE-SHORT-LABEL')
    def _parse_cipher_suite_short_label(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ELLIPTIC-CURVE-REFS')
    @multiple_with_check
    def _parse_elliptic_curve(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('ENCRYPTION-REF')
    def _parse_encryption(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('KEY-EXCHANGE-REFS')
    @multiple_with_check
    def _parse_key_exchange(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('KEY-EXCHANGE-AUTHENTICATION-REFS')
    @multiple_with_check
    def _parse_key_exchange_authentication(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('PRIORITY')
    def _parse_priority(self, xml_element: Element) -> int | None:
        return self._parse_int_node(xml_element)

    @handler('PROPS')
    def _parse_props(self, xml_element: Element) -> TlsCryptoCipherSuiteProps | None:
        parser = TlsCryptoCipherSuitePropsParser()
        return parser.parse_element(xml_element)

    @handler('PSK-IDENTITY')
    def _parse_psk_identity(self, xml_element: Element) -> TlsPskIdentity | None:
        parser = TlsPskIdentityParser()
        return parser.parse_element(xml_element)

    @handler('REMOTE-CERTIFICATE-REF')
    def _parse_remote_certificate(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('SIGNATURE-SCHEME-REFS')
    @multiple_with_check
    def _parse_signature_scheme(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('VERSION')
    def _parse_version(self, xml_element: Element) -> TlsVersionEnum | None:
        return self._parse_enum_node(xml_element, TlsVersionEnum)


class SecOcCryptoServiceMappingParser(IdentifiableParser[SecOcCryptoServiceMapping]):
    _returned_type = SecOcCryptoServiceMapping

    @handler('AUTHENTICATION-REF')
    def _parse_authentication(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CRYPTO-SERVICE-KEY-REF')
    def _parse_crypto_service_key(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('CRYPTO-SERVICE-QUEUE-REF')
    def _parse_crypto_service_queue(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)


class TlsCryptoServiceMappingParser(IdentifiableParser[TlsCryptoServiceMapping]):
    _returned_type = TlsCryptoServiceMapping

    @handler('KEY-EXCHANGE-REFS')
    @multiple_with_check
    def _parse_key_exchange(self, xml_element: Element) -> str | None:
        return self._parse_text_node(xml_element)

    @handler('USE-CLIENT-AUTHENTICATION-REQUEST')
    def _parse_client_auth_request_flag(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('USE-SECURITY-EXTENSION-RECORD-SIZE-LIMIT')
    def _parse_security_extension_record_size_limit_flag(self, xml_element: Element) -> bool | None:
        return self._parse_boolean_node(xml_element)

    @handler('TLS-CIPHER-SUITES')
    @multiple_with_check(expected_name='TLS-CRYPTO-CIPHER-SUITE')
    def _parse_tls_cipher_suite(self, xml_element: Element) -> TlsCryptoCipherSuite | None:
        parser = TlsCryptoCipherSuiteParser()
        return parser.parse_element(xml_element)


class CryptoServiceMappingParserSelector(ParserSelector[CSM]):
    _tag_map = {
        'SEC-OC-CRYPTO-SERVICE-MAPPING': SecOcCryptoServiceMappingParser,
        'TLS-CRYPTO-SERVICE-MAPPING': TlsCryptoServiceMappingParser,
    }
