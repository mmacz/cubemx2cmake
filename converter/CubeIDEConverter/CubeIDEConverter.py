from pathlib import Path
from pprint import pprint
import re
import json


class CubeIDEConverter:
    def __init__(self, project_path: Path, hard_fp: bool = True):
        self.__config = dict()
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
        dirs = list()
        header_count = self.__get_match("HeaderFolderListSize=(.+)", content)
        if header_count.isdigit():
            header_count = int(header_count)
        for i in range(0, header_count):
            dir = self.__get_match(f"HeaderPath#{i}=(.+)", content).split(
                self.__config["name"]
            )[1][1:]
            dirs.append(dir)
        self.__config["include_dirs"] = "\n\t\t".join(dirs)

    def __get_sources(self, content: str):
        sources = list()
        sources_count = self.__get_match("SourceFileListSize=(.+)", content)
        if sources_count.isdigit():
            sources_count = int(sources_count)
        for i in range(0, sources_count):
            src = self.__get_match(f"SourceFiles#{i}=(.+)", content).split(
                self.__config["name"]
            )[1]
            sources.append(src)
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
        self.__touchgfx_path = path.split(self.__config["name"])[1][1:]

        self.__config["core"] = app_config["Application"]["Platform"]

    def __parse_files(self):
        self.__parse_mxproj()
        if self.__has_touchgfx:
            self.__parse_touchgfx()
        # pprint(self.__config)
        pass

    def convert(self):
        self.__parse_files()
        pass
