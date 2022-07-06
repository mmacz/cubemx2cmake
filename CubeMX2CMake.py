#!/bin/python3
import argparse
from pathlib import Path
from converter import CubeMX2CMakeConverter

def validate_args(args: argparse.Namespace) -> bool:
    ioc_file = Path(args.ioc)
    if not ioc_file.is_file():
        raise RuntimeError(f"Project: {ioc_file} is not a file")
    return True

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ioc", help="Path to CubeMX project *.ioc", required=True, type=Path)
    args = parser.parse_args()
    if validate_args(args):
        return args
    else:
        return None

def main() -> None:
    args = parse_args()
    CubeMX2CMakeConverter(args.ioc).convert()

if __name__ == "__main__":
    main()