#!/bin/python3
import argparse
from lib2to3.pytree import convert
from pathlib import Path

from converter.CMakeCubeMX import CMakeCubeMX


def validate_args(args: argparse.Namespace) -> bool:
    project_dir = Path(args.proj)
    if not project_dir.is_dir():
        raise RuntimeError(f"Project: {project_dir} is not a file")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proj", help="Path to project root", required=True, type=Path)
    args = parser.parse_args()
    if validate_args(args):
        return args
    else:
        return None


def main() -> None:
    args = parse_args()
    CMakeCubeMX(args.proj).convert()


if __name__ == "__main__":
    main()
