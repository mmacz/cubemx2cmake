from distutils.core import setup

setup(
    name="cubeide_converter",
    version="1.0",
    license="GPL 3.0",
    author="Marek Mącznik",
    author_email="marek.macznik@gmail.com",
    url="https://github.com/mmacz/cubemx2cmake",
    keywords="STM32 CubeIDE CMake",
    packages=["cubeide_converter"],
    package_dir={"cubeide_converter": "src/cubeide_converter"},
    package_data={
        "cubeide_converter": [
            "cmake/*.cmake",
            "cmake/*.txt",
        ]
    },
    include_package_data=True,
)
