from pathlib import Path
import re
import json
import os


class CubeIDEConverter:
    def __init__(self, project_path: Path, core: str = "m4", hard_fp: bool = True):
        self.__config = dict()
        self.__config["core"] = core
        self.__hard_fp = hard_fp
        self.__validate_project(project_path)
        self.__check_touchgfx(project_path)
        self.__root = project_path

    def __check_touchgfx(self, path: Path) -> bool:
        self.__has_touchgfx = False
        self.__gfx_root = None
        for file in path.iterdir():
            if file.name == "TouchGFX":
                cnt = 0
                for _ in file.iterdir():
                    cnt += 1
                self.__gfx_root = file
                self.__has_touchgfx = True

    def __check_file(self, file: Path):
        if file is not None and not file.is_file():
            raise RuntimeError(f"File {file} does not exist")

    def __validate_project(self, path: Path):
        ioc = None
        self.__mxproj = None
        if path.is_dir():
            for file in path.iterdir():
                if file.suffix == ".ioc":
                    ioc = file
                elif file.stem == ".mxproject":
                    self.__mxproj = file
                elif "FLASH" in file.stem:
                    self.__config["ldscript"] = file.name
            self.__check_file(ioc)
            self.__check_file(self.__mxproj)
            self.__config["name"] = ioc.stem
        else:
            raise RuntimeError(f"Project path {path} is not a directory")

    def __get_match(self, pattern: str, content: str):
        match = re.search(pattern, content)
        return match.group(1) if match else ""

    def __get_split_list(self, data: list, pattern: str = ";"):
        result = data.split(pattern)
        result = [d for d in result if len(d) > 0]
        return result

    def __get_include_dirs(self, content: str):
        inc_dirs = self.__get_match("HeaderPath=(\w.+)", content)
        inc_dirs = self.__get_split_list(inc_dirs)
        self.__config["include_dirs"] = "\n\t\t".join(inc_dirs)

    def __get_sources(self, content: str):
        sources = self.__get_match("SourceFiles=(\w.+)", content)
        sources = self.__get_split_list(sources)
        sources = [src for src in sources if Path(self.__root / src).is_file()]
        self.__config["sources"] = "\n\t\t".join(sources)

    def __get_cdefines(self, content: str):
        defines = self.__get_match("CDefines=(.+)", content)
        defines = self.__get_split_list(defines)
        defines = list(dict.fromkeys(defines))
        defines = [f"-D{d}" for d in defines]
        self.__config["cdefs"] = "\n\t\t".join(defines)

    def __parse_mxproj(self):
        content = "".join(open(self.__mxproj, "r").readlines())
        self.__get_include_dirs(content)
        self.__get_sources(content)
        self.__get_cdefines(content)

    def __parse_touchgfx(self):
        file_name = self.__gfx_root / str(self.__config["name"] + ".touchgfx")
        if not file_name.is_file():
            raise RuntimeError("Please generate TouchGFX project first")
        content = "".join(open(file_name, "r").readlines())
        app_config = json.loads(content)

        path = app_config["Application"]["TouchGfxPath"].replace(
            "..", str(self.__root.absolute())
        )
        self.__touchgfx_path = path.split(self.__config["name"])
        if len(self.__touchgfx_path) > 1:
            self.__touchgfx_path = self.__touchgfx_path[1][1:]

        self.__config["core"] = app_config["Application"]["Platform"]

    def __get_flash_info(self) -> tuple:
        ldscript = self.__root / self.__config["ldscript"]
        content = "".join(open(ldscript, "r").readlines())
        flash_matcher = re.search(
            "FLASH\s+\(rx\)\s+:\s+ORIGIN = (0x[a-fA-F0-9]+),\s+LENGTH\s+=\s+(\d+.)",
            content,
        )
        origin = flash_matcher.group(1)
        size = flash_matcher.group(2).lower()
        self.__config["flash_origin"] = origin
        self.__config["flash_size"] = size

    def __parse_files(self):
        self.__parse_mxproj()
        self.__get_flash_info()
        if self.__has_touchgfx:
            self.__parse_touchgfx()

    def __prepare_toolchain_file(self, templates_dir: Path):
        fp = "hf" if self.__hard_fp else ""
        toolchain_file = f"armv7{fp}-toolchain.cmake"
        self.__config["toolchain"] = toolchain_file

        toolchain_file = templates_dir / toolchain_file
        content = "".join(open(toolchain_file, "r").readlines())
        content = content.replace("@CORE@", self.__config["core"])
        return content

    def __prepare_stlink_file(self, templates_dir: Path):
        stlink_file = templates_dir / "stlink.cmake"
        content = "".join(open(stlink_file, "r").readlines())
        content = content.replace("@PROJECT@", self.__config["name"])
        content = content.replace("@FLASH_SIZE@", self.__config["flash_size"])
        content = content.replace("@FLASH_ORIGIN@", self.__config["flash_origin"])
        return content

    def __prepare_cmakelists_file(self, templates_dir: Path):
        cmakelists_file = templates_dir / "CMakeLists.txt"
        content = "".join(open(cmakelists_file, "r").readlines())
        content = content.replace("@TOOLCHAIN_FILE@", self.__config["toolchain"])
        content = content.replace("@LINKER_SCRIPT@", self.__config["ldscript"])
        content = content.replace("@PROJECT@", self.__config["name"])
        content = content.replace("@SOURCES@", self.__config["sources"])
        content = content.replace("@INC_DIRS@", self.__config["include_dirs"])
        content = content.replace("@C_DEFS@", self.__config["cdefs"])
        return content

    def __handle_touchgfx(self, content: str, templates_dir: Path):
        if not self.__has_touchgfx:
            start_block_idx = content.find("@TOUCHGFX_START@")
            end_block_idx = content.find("@TOUCHGFX_END@")
            end_block_len = len("@TOUCHGFX_END@") + 1
            content = (
                content[:start_block_idx] + content[end_block_idx + end_block_len :]
            )
            content = content.replace("@TOUCHGFX_LIB@", "")
            return content, None
        else:
            content = content.replace("@TOUCHGFX_START@", "")
            content = content.replace("@TOUCHGFX_END@", "")
            content = content.replace("@TOUCHGFX_LIB@", "\n\t\tST::TouchGFX")

            finder_template_file = templates_dir / "FindTouchGFX.cmake"
            finder_template = "".join(open(finder_template_file, "r").readlines())

            core = {"m4": "m4f", "m0": "m0", "m3": "m33"}[self.__config["core"]]
            fp = "-float-abi-hard" if self.__hard_fp else ""
            finder_template = finder_template.replace(
                "@TOUCHGFX_MIDDLEWARES@", self.__touchgfx_path
            )
            gfx_root = str(self.__gfx_root).split(self.__config["name"])
            if len(gfx_root) > 1:
                gfx_root = gfx_root[1][1:]
            else:
                gfx_root = gfx_root[0]
            finder_template = finder_template.replace("@TOUCHGFX_ROOT@", gfx_root)
            finder_template = finder_template.replace("@CORE@", core)
            finder_template = finder_template.replace("@HARD_FP@", fp)

            return content, finder_template

    def __convert_project(self):
        target_cmake_dir = self.__root / "cmake"
        if not target_cmake_dir.is_dir():
            os.mkdir(target_cmake_dir)

        cmake_templates_dir = Path(__file__).parent / "cmake"
        target_toolchain_content = self.__prepare_toolchain_file(cmake_templates_dir)
        target_toolchain = target_cmake_dir / self.__config["toolchain"]
        with open(target_toolchain, "w") as f:
            f.write(target_toolchain_content)

        target_stlink_content = self.__prepare_stlink_file(cmake_templates_dir)
        target_stlink = target_cmake_dir / "stlink.cmake"
        with open(target_stlink, "w") as f:
            f.write(target_stlink_content)

        target_cmakelists_content = self.__prepare_cmakelists_file(cmake_templates_dir)
        target_cmakelists = self.__root / "CMakeLists.txt"

        target_cmakelists_content, touchgfx_finder = self.__handle_touchgfx(
            target_cmakelists_content, cmake_templates_dir
        )

        if touchgfx_finder is not None:
            target_touchgfx_finder = target_cmake_dir / "FindTouchGFX.cmake"
            with open(target_touchgfx_finder, "w") as f:
                f.write(touchgfx_finder)

        with open(target_cmakelists, "w") as f:
            f.write(target_cmakelists_content)

    def convert(self):
        self.__parse_files()
        self.__convert_project()
