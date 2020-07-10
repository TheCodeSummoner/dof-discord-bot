"""
The installation performs the following:

    - Get all meta-information
    - Install all dependencies
    - Get the top level `dof_discord_bot` package
    - Copy all sources
    - Copy some additional files

Of course, alternatively, you can execute the code pulled from github directly.
"""
import os
import json
import setuptools

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

setuptools.setup(
    name=metadata["__title__"],
    description=metadata["__description__"],
    version=metadata["__version__"],
    author=metadata["__lead__"],
    author_email=metadata["__email__"],
    maintainer=metadata["__lead__"],
    maintainer_email=metadata["__email__"],
    url=metadata["__url__"],
    license="MIT License",
    packages=setuptools.find_namespace_packages(),
    package_data={"dof_discord_bot": PACKAGE_DATA},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        "discord",
        "pyyaml",
        "python-dotenv"
    ],
    python_requires=">=3.6",
)
