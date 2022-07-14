from setuptools import setup, find_packages

setup(
    name="CubeIDEConverter",
    version="1.0",
    license="GPL 3.0",
    author="Marek Mącznik",
    author_email="marek.macznik@gmail.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/mmacz/cubemx2cmake",
    keywords="STM32 CubeIDE CMake",
)
