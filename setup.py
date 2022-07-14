from distutils.core import setup

setup(
    name="CubeIDEConverter",
    version="1.0",
    license="GPL 3.0",
    author="Marek Mącznik",
    author_email="marek.macznik@gmail.com",
    url="https://github.com/mmacz/cubemx2cmake",
    keywords="STM32 CubeIDE CMake",
    packages=["CubeIDEConverter"],
    package_dir={"CubeIDEConverter": "src/CubeIDEConverter"},
    package_data={
        "CubeIDEConverter": [
            "cmake/*.cmake",
            "cmake/*.txt",
        ]
    },
    include_package_data=True,
)
