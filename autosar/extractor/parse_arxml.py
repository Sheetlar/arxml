from argparse import ArgumentParser
from pathlib import Path

from autosar.extractor.system import ExtractedSystem
from autosar.misc import setup_logger
from autosar.workspace import Workspace


def parse_arxml(arxml_file_path: Path):
    ws = Workspace(version=4.0, patch=None, schema=None)
    ws.load_xml(arxml_file_path)
    extracted_systems = tuple(map(ExtractedSystem, ws.systems))
    return extracted_systems


if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument('arxml_path')
    parsed_args = arg_parser.parse_args()
    setup_logger()
    parse_arxml(Path(parsed_args.arxml_path))
