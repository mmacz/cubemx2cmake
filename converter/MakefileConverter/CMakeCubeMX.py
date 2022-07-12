from distutils.log import warn
from pathlib import Path
import warnings
from converter.MakefileConverter import MakefileConverter


class CMakeCubeMX:
    def __init__(self, proj: Path):
        """Create CMake coverter from CubeMX."""
        self.__proj_root = proj
        if not self.__proj_root.is_dir():
            raise RuntimeError(f"Path: {self.__proj_root} is not directory")
        self.__config = dict()

    def __handle_makefile(self) -> bool:
        """Try to parse Makefile generated projet."""
        return MakefileConverter(self.__proj_root).convert()

    def convert(self) -> bool:
        """Convert CubeMX generated project to CMake.

        For now it supports only Makefile projects.
        """
        if not self.__handle_makefile():
            warnings.warn("Makefile not present or parsing error.")
            return False
        return True
