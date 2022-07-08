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

    def __parse_makefile(self) -> bool:
        """Try to parse Makefile generated projet."""
        self.__config = MakefileParser(self.__proj_root).parse()
        print(self.__config)
        return self.__config is not None

    def convert(self):
        """Convert CubeMX generated project to CMake."""
        if not self.__parse_makefile():
            warnings.warn("Makefile not present.")
        pass
