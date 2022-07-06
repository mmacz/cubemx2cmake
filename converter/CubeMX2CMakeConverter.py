from pathlib import Path
import re

class CubeMX2CMakeConverter():
    def __init__(self, ioc: Path):
        self.__ioc = ioc
        self.__is_makefile = self.__check_makefile()
        if not self.__is_makefile:
            raise RuntimeError(f"Only Makefile project is supported for now.")

    def __check_makefile(self) -> bool:
        makefile_path = self.__ioc.parent / "Makefile"
        return makefile_path.is_file()

    def __parse_ioc(self) -> dict:
        ioc_content = "".join(open(str(self.__ioc), 'r').readlines())
        project_name_matcher = re.search("ProjectManager.ProjectName=(.+)", ioc_content)
        series_matcher = re.search("Mcu.Family=(.+)", ioc_content)
        device_id_matcher = re.search("ProjectManager.DeviceId=(.+)", ioc_content)

        project_name = project_name_matcher.group(1)
        series = series_matcher.group(1)
        device_id = device_id_matcher.group(1)
        short_device_id = device_id[:len(series)+2]
        return {
            "project": project_name,
            "series": series,
            "device_id": device_id,
            "short_device_id": short_device_id
        }

    def __get_c_flags(self, makefile_content: str) -> str:
        cpu_matcher = re.search("CPU = (.+)", makefile_content)
        fpu_matcher = re.search("FPU = (.+)", makefile_content)
        float_abi_matcher = re.search("FLOAT-ABI = (.+)", makefile_content)

        cpu = cpu_matcher.group(1)
        fpu = fpu_matcher.group(1)
        float_abi = float_abi_matcher.group(1)
        return f"{cpu} -mthumb {fpu} {float_abi}"

    def __get_c_defines(self, makefile_content: str) -> str:
        c_defs_matcher = re.search("C_DEFS = (.+)\n-D(.+)\n-D(.+)", makefile_content)
        c_defs = "".join(c_defs_matcher.groups()).split("\\")[1:]
        defs = ""
        for _def in c_defs:
            defs += f"-D{_def}"
        return defs.replace("  ", " ")

    def __get_ldscript(self, makefile_content: str) -> str:
        ldscript_matcher = re.search("LDSCRIPT = (.+)", makefile_content)
        return ldscript_matcher.group(1)
    
    def __get_libs(self, makefile_content: str) -> str:
        libs_matcher = re.search("LIBS = (.+)", makefile_content)
        libs = libs_matcher.group(1).replace("-l", "").split(" ")[:-1]
        return "\n".join(f"\t\t{lib}" for lib in libs)

    def __get_c_sources(self, makefile_content: str) -> str:
        """Get C source files that are needed by the project.
        
        This function is little hacky, it assumes that the generated C sources are always listed
        before ASM sources.
        """
        c_sources_pos = makefile_content.find("# C sources")
        asm_sources_pos = makefile_content.find("# ASM sources")
        sources = "".join(makefile_content[c_sources_pos:asm_sources_pos].split("\n")[2:-2]).replace(" ", "")
        sources = sources.split("\\")
        sources = "\n".join(f"\t\t{source}" for source in sources)
        return sources
    
    def __get_startup(self, makefile_content: str) -> str:
        startup_matcher = re.search("startup_stm32(.+)", makefile_content)
        return startup_matcher.group(0)

    def __get_c_includes(self, makefile_content: str) -> str:
        """Get C include directories."""
        c_includes_pos = makefile_content.find("# C includes")
        compile_flags_pos = makefile_content.find("# compile gcc flags")
        includes = "".join(makefile_content[c_includes_pos:compile_flags_pos].split("\n")[2:-2]).replace(" ", "").replace("-I", "")
        includes = includes.split("\\")
        includes = "\n".join(f"\t\t{inc}" for inc in includes)
        return includes

    def __get_compilation_info(self, makefile_content: str) -> dict:
        c_flags = self.__get_c_flags(makefile_content)
        c_defs = self.__get_c_defines(makefile_content)
        ldscript = self.__get_ldscript(makefile_content)
        libs = self.__get_libs(makefile_content)
        sources = self.__get_c_sources(makefile_content)
        includes = self.__get_c_includes(makefile_content)
        startup = self.__get_startup(makefile_content)
        return {
            "flags": c_flags,
            "defs": c_defs,
            "script": ldscript,
            "libs": libs,
            "sources": sources,
            "includes": includes,
            "startup": startup,
        }
        
    def __parse_makefile(self) -> dict:
        makefile_path = self.__ioc.parent / "Makefile"
        makefile_content = "".join(open(makefile_path, 'r').readlines())
        return self.__get_compilation_info(makefile_content)

    def __fill_template(self, proj_info: dict, comp_info: dict) -> str:
        cmakelists_template = Path(__file__).parent / "CMakeLists.txt"
        template_content = "".join(open(cmakelists_template, 'r').readlines())
        template_content = template_content.replace("@PROJECT@", proj_info['project'])
        template_content = template_content.replace("@SERIES@", proj_info['series'])
        template_content = template_content.replace("@CFLAGS@", comp_info['flags'])
        template_content = template_content.replace("@LINKER_SCRIPT@", comp_info['script'])
        template_content = template_content.replace("@C_DEFS@", comp_info['defs'])
        template_content = template_content.replace("@SOURCES@", comp_info['sources'])
        template_content = template_content.replace("@INCLUDES@", comp_info['includes'])
        template_content = template_content.replace("@STARTUP@", comp_info['startup'])
        return template_content.replace("@LIBS@", comp_info['libs'])
    
    def convert(self) -> None:
        project_info = self.__parse_ioc()
        compilation_info = self.__parse_makefile()
        cmakelists_content = self.__fill_template(project_info, compilation_info)
        output_cmakelists = self.__ioc.parent / "CMakeLists.txt"
        with open(output_cmakelists, 'w') as f:
            f.write(cmakelists_content)
