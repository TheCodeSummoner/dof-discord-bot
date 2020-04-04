"""
Dof Discord Bot
===============

The installation performs the following:

    1. Install all dependencies
    2. Get the top level `dof_discord_bot`"` package
    3. Copy all sources
    4. Copy some additional files

Of course, alternatively, you can execute the code pulled from github directly.
"""
import os
import setuptools

# Fetch the root folder to specify absolute paths to the files to include
ROOT = os.path.normpath(os.path.dirname(__file__))

# Specify which files should be added to the installation
PACKAGE_DATA = [
    os.path.join(ROOT, "dof_discord_bot", "log", "config.json"),
    os.path.join(ROOT, "dof_discord_bot", "log", "README.md"),
    os.path.join(ROOT, "dof_discord_bot", "src", "README.md"),
    os.path.join(ROOT, "LICENSE"),
    os.path.join(ROOT, "README.md")
]


setuptools.setup(
    name="dof_discord_bot",
    description="Defender's of Faith discord bot",
    version="1.0.0",
    author="Florianski Kacper",
    maintainer="Florianski Kacper",
    maintainer_email="kacper.florianski@gmail.com",
    url="https://github.com/TheCodeSummoner/dof-discord-bot",
    license="MIT License",
    packages=setuptools.find_namespace_packages(),
    package_data={"dof_discord_bot": PACKAGE_DATA},
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
