"""
Dof Discord Bot
===============

The installation performs the following:

    1. Install all dependencies
    2. Get the top level `dof_discord_bot` package
    3. Copy all sources
    4. Copy some additional files

Of course, alternatively, you can execute the code pulled from github directly.
"""
import os
import json
import setuptools


def get_meta_information(path: str) -> tuple:
    """
    TODO
    """
    with open(path) as f:
        content = f.read()
        fields = tuple(content[content.find(field):].split("\n")[0][len(field) + 3:].replace("\"", "").strip()
                       for field in ["__name__", "__description__", "__version__", "__lead__", "__email__", "__url__"])
        return fields


# Fetch the root folder to specify absolute paths to the files to include
ROOT = os.path.normpath(os.path.dirname(__file__))

# Specify which files should be added to the installation
PACKAGE_DATA = [
    os.path.join(ROOT, "dof_discord_bot", "res", "strings.yaml"),
    os.path.join(ROOT, "dof_discord_bot", "res", "meta.json"),
    os.path.join(ROOT, "dof_discord_bot", "res", "config.json"),
    os.path.join(ROOT, "dof_discord_bot", "log", ".keep"),
]

with open(os.path.join(ROOT, "dof_discord_bot", "res", "meta.json")) as f:
    metadata = json.load(f)

__name__ = metadata["__name__"]
__version__ = metadata["__version__"]
__description__ = metadata["__description__"]
__lead__ = metadata["__lead__"]
__email__ = metadata["__email__"]
__url__ = metadata["__url__"]

setuptools.setup(
    name=__name__,
    description=__description__,
    version=__version__,
    author=__lead__,
    maintainer=__lead__,
    maintainer_email=__email__,
    url=__url__,
    license="MIT License",
    packages=setuptools.find_namespace_packages(),
    package_data={"dof_discord_bot": PACKAGE_DATA},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        "discord",
        "pyyaml"
    ],
    python_requires=">=3.8.1",
)
