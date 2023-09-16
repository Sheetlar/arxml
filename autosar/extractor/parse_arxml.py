from argparse import ArgumentParser
from pathlib import Path

import autosar
from autosar.extractor.system_extractor import SystemExtractor
from autosar.has_logger import setup_logger
from autosar.system import System


def parse_arxml(arxml_file_path: Path):
    ws = autosar.workspace()
    ws.load_xml(arxml_file_path)
    systems = (e for p in ws.packages for e in p.elements if isinstance(e, System))
    extracted_systems = tuple(map(SystemExtractor.extract_system, systems))
    return extracted_systems


if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument('arxml_path')
    parsed_args = arg_parser.parse_args()
    setup_logger()
    parse_arxml(Path(parsed_args.arxml_path))
