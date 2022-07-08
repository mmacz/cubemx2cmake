from distutils.log import warn
from pathlib import Path
import warnings
from converter.MakefileParser import MakefileParser


class CMakeCubeMX:
    def __init__(self, proj: Path):
        """Create CMake coverter from CubeMX."""
        self.__proj_root = proj
        if not self.__proj_root.is_dir():
            raise RuntimeError(f"Path: {self.__proj_root} is not directory")
        self.__config = dict()

    def __parse_makefile(self) -> dict:
        """Try to parse Makefile generated projet."""
        return MakefileParser(self.__proj_root).parse()

    def convert(self):
        """Convert CubeMX generated project to CMake."""
        config = self.__parse_makefile()
        if config is None:
            warnings.warn("Makefile not present.")
        print(config)
