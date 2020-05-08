# Dof discord bot

Defenders of Faith's discord bot, as used in [here][1].

Visit [our website][2] or this [Taleworlds thread][3] for more information about DoF.

## Getting Started

These instructions will help you understand how to get the project up and running for development and testing purposes.
To deploy the system to your own discord server, follow the standard Discord developer guidelines.

### Prerequisites

1. You must have Python 3.6 or higher installed. You can get it from the [official website][4].
2. You must provide a Discord token - either through an environment variable `DOF_TOKEN` or by creating the `token.txt`
file in `res` directory - for more information following the instructions when attempting to run the bot without the
token.
3. You must either install the package (see below) or make sure to install all dependencies (see `setup.py`).

### Installing

Installation is optional, as you can simply run the code directly downloaded from github, as long as all prerequisites
are met. However, to make sure the files are in correct place and all dependencies are installed, you can run the
following `pip` command:

```
pip install git+https://github.com/TheCodeSummoner/dof-discord-bot.git
```

To check that it has been successfully installed, check that you can import and use the package in your python console,
or run the following command:

```
python -c "import dof_discord_bot; print(f'{dof_discord_bot.__title__} v{dof_discord_bot.__version__}')"
```

### Usage

You can run the code in a few ways, feel free to pick the most appropriate one from the list below. Keep in mind that
the logs files will be created in different directories, depending on which method do you choose (either in
`site-packages`-specific folder, or in `log` folder directly in the downloaded files).

#### Run from python console

You can import the `dof_discord_bot` package and call the `run` method to run the bot:

```python
import dof_discord_bot

dof_discord_bot.run()
```

#### Run main directly

Python provides ways to execute packages by providing the `__main__.py` file. You can therefore run:

```
python <path>/dof-discord-bot/dof_discord_bot
```

or:

```
python <path>/dof-discord-bot/dof_discord_bot.__main__.py
```

#### Run installed files

If you installed the package by following the instructions above (so with the `pip` command), you can simply run:

```
python -m dof_discord_bot
```

## Contributing

To contribute you can raise GitHub issues, submit a pull request with some code changes or ping me on [DoF discord][1].

## License

This project is licensed under the MIT License - see the [LICENSE.md][5] file for details

## Acknowledgments

Thanks to the [Python discord bot][6] for open-sourcing their code and therefore providing an excellent learning
resource about Python discord API.

[1]: https://discord.com/invite/BRRfqqZ
[2]: https://dofesports.wixsite.com/defenders-of-faith
[3]: https://forums.taleworlds.com/index.php?threads/dof-defenders-of-faith-international-clan-decade-of-faith-we-are-recruiting.417098/
[4]: https://www.python.org/downloads/
[5]: LICENSE
[6]: https://github.com/python-discord/bot
