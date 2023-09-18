from autosar.extractor.common import ScalableDataType

e2e_profiles = {
    'PROFILE_04': {
        'E2E_length': ScalableDataType('UINT16', '>u2', 1),
        'E2E_counter': ScalableDataType('UINT16', '>u2', 1),
        'E2E_data_id': ScalableDataType('UINT32', '>u4', 1),
        'E2E_crc': ScalableDataType('UINT32', '>u4', 1),
    },
    'PROFILE_05': {
        'E2E_crc': ScalableDataType('UINT16', '>u2', 1),
        'E2E_counter': ScalableDataType('UINT8', '>u1', 1),
    },
    'PROFILE_07': {
        'E2E_crc': ScalableDataType('UINT64', '>u8', 1),
        'E2E_length': ScalableDataType('UINT32', '>u4', 1),
        'E2E_counter': ScalableDataType('UINT32', '>u4', 1),
        'E2E_data_id': ScalableDataType('UINT32', '>u4', 1),
    },
}
