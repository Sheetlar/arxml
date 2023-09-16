from autosar.extractor.common import ScalableDataType

e2e_profiles = {
    'PROFILE_04': {
        'E2E_length': ScalableDataType('UINT16', 'UINT16', 1),
        'E2E_counter': ScalableDataType('UINT16', 'UINT16', 1),
        'E2E_data_id': ScalableDataType('UINT32', 'UINT32', 1),
        'E2E_crc': ScalableDataType('UINT32', 'UINT32', 1),
    },
    'PROFILE_05': {
        'E2E_crc': ScalableDataType('UINT16', 'UINT16', 1),
        'E2E_counter': ScalableDataType('UINT8', 'UINT8', 1),
    },
    'PROFILE_07': {
        'E2E_crc': ScalableDataType('UINT64', 'UINT64', 1),
        'E2E_length': ScalableDataType('UINT32', 'UINT32', 1),
        'E2E_counter': ScalableDataType('UINT32', 'UINT32', 1),
        'E2E_data_id': ScalableDataType('UINT32', 'UINT32', 1),
    },
}
