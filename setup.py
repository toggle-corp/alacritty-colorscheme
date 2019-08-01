from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()

with open("LICENSE-APACHE") as f:
    license = f.read()

setup(
    name="alacritty-colorscheme",
    version="0.1.0",
    description="Change colorscheme of alacritty with ease.",
    long_description=readme,
    url="",
    license=license,
    install_requires=[],
    packages=find_packages(exclude=("tests", "docs")),
    entry_points = {
        "console_scripts": [
            "alacritty-colorscheme=alacritty_colorscheme.cli:main",
        ]
    }
)

