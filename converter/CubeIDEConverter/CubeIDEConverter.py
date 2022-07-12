from pathlib import Path


class CubeIDEConverter:
    def __init__(self, project_path: Path):
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
                if cnt == 3:  # App, target, app template
                    raise RuntimeError(
                        "Please generate TouchGFX project first using Designer"
                    )

    def __check_file(self, file: Path):
        if file is not None and not file.is_file():
            raise RuntimeError(f"File {file} does not exist")
        return

    def __validate_project(self, path: Path):
        self.__ioc = None
        self.__mxproj = None
        if path.is_dir():
            for file in path.iterdir():
                if file.suffix == ".ioc":
                    self.__ioc = file
                if file.suffix == ".mxproject":
                    self.__mxproj = file
            self.__check_file(self.__ioc)
            self.__check_file(self.__mxproj)
        else:
            raise RuntimeError(f"Project path {path} is not a directory")
