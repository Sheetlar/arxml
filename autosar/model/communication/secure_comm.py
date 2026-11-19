from typing import Iterable

from autosar.model.ar_object import ArObject
from autosar.model.base import Identifiable
from autosar.model.element import Element
from autosar.model.enums import (
    CryptoServiceKeyGenerationEnum,
    CryptoCertificateAlgorithmFamilyEnum,
    CryptoCertificateFormatEnum,
)
from autosar.model.value_spec import ValueSpecification


class SecureCommunicationAuthenticationProps(Identifiable):
    def __init__(
            self,
            auth_info_tx_length: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.auth_info_tx_length = auth_info_tx_length


class SecureCommunicationFreshnessProps(Identifiable):
    def __init__(
            self,
            freshness_counter_sync_attempts: int | None = None,
            freshness_timestamp_time_period_factor: int | None = None,
            freshness_value_length: int | None = None,
            freshness_value_tx_length: int | None = None,
            use_freshness_timestamp: bool | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.freshness_counter_sync_attempts = freshness_counter_sync_attempts
        self.freshness_timestamp_time_period_factor = freshness_timestamp_time_period_factor
        self.freshness_value_length = freshness_value_length
        self.freshness_value_tx_length = freshness_value_tx_length
        self.use_freshness_timestamp = use_freshness_timestamp


class SecureCommunicationPropsSet(Element):
    def __init__(
            self,
            authentication_props: Iterable[SecureCommunicationAuthenticationProps] | None = None,
            freshness_props: Iterable[SecureCommunicationFreshnessProps] | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.authentication_props = self._set_parent(authentication_props)
        self.freshness_props = self._set_parent(freshness_props)

    @property
    def _findable_children(self) -> Iterable[ArObject]:
        yield from self.authentication_props
        yield from self.freshness_props


class CryptoServicePrimitive(Element):
    def __init__(
            self,
            algorithm_family: str | None = None,
            algorithm_secondary_family: str | None = None,
            algorithm_mode: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.algorithm_family = algorithm_family
        self.algorithm_secondary_family = algorithm_secondary_family
        self.algorithm_mode = algorithm_mode


class CryptoServiceKey(Element):
    def __init__(
            self,
            length: int,
            algorithm_family: str | None = None,
            development_value: ValueSpecification | None = None,
            key_generation: CryptoServiceKeyGenerationEnum | None = None,
            key_storage_type: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.length = length
        self.algorithm_family = algorithm_family
        self.development_value = development_value
        self.key_generation = key_generation
        self.key_storage_type = key_storage_type


class CryptoServiceQueue(Element):
    def __init__(
            self,
            queue_size: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.queue_size = queue_size


class CryptoEllipticCurveProps(Element):
    def __init__(
            self,
            named_curve_id: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.named_curve_id = named_curve_id


class CryptoSignatureScheme(Element):
    def __init__(
            self,
            signature_scheme_id: int | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.signature_scheme_id = signature_scheme_id


class CryptoServiceCertificate(Element):
    def __init__(
            self,
            algorithm_family: CryptoCertificateAlgorithmFamilyEnum | None = None,
            fmt: CryptoCertificateFormatEnum | None = None,
            maximum_length: int | None = None,
            next_higher_certificate_ref: str | None = None,
            server_name_identification: str | None = None,
            *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.algorithm_family = algorithm_family
        self.format = fmt
        self.maximum_length = maximum_length
        self.next_higher_certificate_ref = next_higher_certificate_ref
        self.server_name_identification = server_name_identification
