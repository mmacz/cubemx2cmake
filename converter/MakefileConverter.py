from pathlib import Path
from pprint import pprint
import re
import shutil

import sys


class MakefileConverter:
    def __init__(self, path: Path):
        self.__file = path / "Makefile"
        self.__is_valid = self.__file.is_file()
        if self.__is_valid:
            self.__read()
        self.__config = dict()
        self.__is_touchgfx = self.__check_touchgfx_project()

    def __check_touchgfx_project(self) -> bool:
        touchgfx_dir = self.__file.parent / "TouchGFX"
        if not touchgfx_dir.is_dir():
            self.__config["touchgfx"] = ""
            return False

    def __read(self):
        self.__content = "".join(open(self.__file, "r").readlines())

    def __extract_project_name(self):
        project_name_matcher = re.search("TARGET = (.+)", self.__content)
        self.__config["name"] = project_name_matcher.group(1)

    def __extract_mcu(self):
        cpu_matcher = re.search("CPU = (.+)", self.__content)
        fpu_matcher = re.search("FPU = (.+)", self.__content)
        float_abi_matcher = re.search("FLOAT-ABI = (.+)", self.__content)

        cpu = cpu_matcher.group(1)
        fpu = fpu_matcher.group(1)
        float_abi = float_abi_matcher.group(1)

        mcu = f"{cpu} {fpu} {float_abi} -mthumb"
        self.__config["mcu"] = mcu

    def __extract_c_defines(self):
        c_defs = re.findall(r"-D(\w+)", self.__content)
        c_defs = [f"-D{cdef}" for cdef in c_defs]
        c_defs = "\n\t\t".join(c_defs)
        self.__config["c_defs"] = c_defs

    def __extract_c_include_paths(self):
        inc_paths = re.findall(r"-I(.+)", self.__content)
        inc_paths = [str(path).replace(" \\", "") for path in inc_paths]
        inc_paths = "\n\t\t".join(inc_paths)
        self.__config["inc_paths"] = inc_paths

    def __extract_ld_script(self):
        ld_script_matcher = re.search("LDSCRIPT = (.+)", self.__content)
        self.__config["ldscript"] = ld_script_matcher.group(1)

    def __extract_sources(self, lang: str):
        content_split = self.__content.split("\n")
        idx = [
            idx
            for idx, element in enumerate(content_split)
            if f"{lang}_SOURCES" in element
        ][0] + 1

        sources = list()
        for line in content_split[idx:]:
            if line == "":
                break
            line = line.replace("\\", "").replace(" ", "")
            sources.append(line)
        sources = "\n\t\t".join(sources)
        self.__config[f"{str.lower(lang)}_srcs"] = sources

    def __extract_libs(self):
        libs_matcher = re.search("LIBS = (.+)", self.__content)
        libs = libs_matcher.group(1).split()
        libs = [lib.replace("-l", "\t\t") for lib in libs]
        libs = "\n".join(libs)
        self.__config["libs"] = libs

    def __set_compilation_flags(self):
        asm_flags = f"{self.__config['mcu']}"
        c_flags = f"{self.__config['mcu']}"
        cpp_flags = f"{self.__config['mcu']}"
        flags = dict()
        flags["asm"] = asm_flags
        flags["c"] = c_flags
        flags["cpp"] = cpp_flags
        self.__config["comp_flags"] = flags

    def __set_linker_flags(self):
        ld_flags = f"{self.__config['mcu']}"
        self.__config["ldflags"] = ld_flags

    def __parse_touchgfx_app(self):
        print(f"TODO: Implement: {__file__}: {sys._getframe().f_code.co_name}")
        pass

    def __parse(self) -> bool:
        """Parse Makefile."""
        if self.__is_valid:
            self.__extract_project_name()
            self.__extract_mcu()
            self.__extract_c_defines()
            self.__extract_c_include_paths()
            self.__extract_ld_script()
            self.__extract_sources("C")
            self.__extract_sources("ASM")
            self.__extract_libs()
            self.__set_compilation_flags()
            self.__set_linker_flags()
            if self.__is_touchgfx:
                self.__parse_touchgfx_app()

            pprint(self.__config)
            return True
        else:
            return False

    def __handle_template(self) -> None:
        template_file = Path(__file__).parent / "CMakeLists.txt"
        template_content = "".join(open(template_file, "r").readlines())
        template_content = template_content.replace(
            "@LINKER_SCRIPT@", self.__config["ldscript"]
        )
        template_content = template_content.replace("@PROJECT@", self.__config["name"])
        template_content = template_content.replace(
            "@ASM_SOURCES@", self.__config["asm_srcs"]
        )
        template_content = template_content.replace(
            "@C_SOURCES@", self.__config["c_srcs"]
        )
        template_content = template_content.replace(
            "@INC_DIRS@", self.__config["inc_paths"]
        )
        template_content = template_content.replace("@C_DEFS@", self.__config["c_defs"])
        template_content = template_content.replace(
            "@CFLAGS@", self.__config["comp_flags"]["c"]
        )
        template_content = template_content.replace(
            "@LDFLAGS@", self.__config["ldflags"]
        )
        template_content = template_content.replace("@LIBS@", self.__config["libs"])
        self.__cmake_project = template_content

    def __create_project(self) -> bool:
        cmake_lists_file = self.__file.parent / "CMakeLists.txt"
        with open(cmake_lists_file, "w") as f:
            f.write(self.__cmake_project)
        toolchain_file = "armv7-toolchain.cmake"
        shutil.copy(
            Path(__file__).parent / toolchain_file, self.__file.parent / toolchain_file
        )
        stlink_file = "stlink.cmake"
        shutil.copy(
            Path(__file__).parent / stlink_file, self.__file.parent / stlink_file
        )

        return True

    def convert(self) -> bool:
        """Extract project information from Makefile and create target CMake project."""
        if self.__parse():
            self.__handle_template()
            return self.__create_project()
        else:
            return False
