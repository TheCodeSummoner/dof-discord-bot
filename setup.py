"""
Dof Discord Bot
===============

The installation performs the following:

    1. Install all dependencies
    2. Create the top level "dof-discord-bot" directory
    3. Copy sources
    4. Copy some additional files

Of course, alternatively, you can execute the code pulled from github directly.
"""
import setuptools
import os

# Fetch the root folder to specify absolute paths to the files to include
ROOT = os.path.normpath(os.path.dirname(__file__))

# Specify which directories and files should be added to the installation
DIRS = [
    os.path.join(ROOT, "log"),
]
FILES = [
    os.path.join(ROOT, "LICENSE"),
    os.path.join(ROOT, "README.md")
]


def _get_package_data() -> list:
    """
    Helper function used to fetch the relevant files to add to the package.

    :return: List of file paths
    """
    data = []

    # Recursively copy the directories to include
    for _ in DIRS:
        for root_dir, _, files in os.walk(_):
            for file in files:
                path = os.path.join(root_dir, file)
                if "__pycache__" not in path:
                    data.append(path)

    # Copy the files to include
    for file in FILES:
        data.append(file)

    return data


# By renaming the packages, the correct structure is ensured
packages_renamed = ["dof-discord-bot"] + [package.replace("src", "dof-discord-bot.src")
                                          for package in setuptools.find_packages()]
package_dirs_renamed = {package: package.replace("dof-discord-bot.", "").replace(".", "/")
                        for package in packages_renamed}
package_dirs_renamed["dof-discord-bot"] = "."
if "tests" in package_dirs_renamed:
    del package_dirs_renamed["tests"]

# Non-packaged files which will be included in the global package
package_data = _get_package_data()

setuptools.setup(
    name="dof-discord-bot",
    description="Defender's of Faith discord bot",
    version="1.0.0",
    author="Florianski Kacper",
    maintainer="Florianski Kacper",
    maintainer_email="kacper.florianski@gmail.com",
    url="https://github.com/TheCodeSummoner/dof-discord-bot",
    license="MIT License",
    packages=packages_renamed,
    package_dir=package_dirs_renamed,
    package_data={"dof-discord-bot": package_data},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        "discord"
    ],
    python_requires=">=3.8.1",
)
