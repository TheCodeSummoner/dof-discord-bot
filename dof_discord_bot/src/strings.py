"""
Formattable strings, loaded from a YAML file.
"""
import os as _os
import yaml as _yaml
from .constants import RES_DIR as _RES_DIR
from .logger import Log as _Log

with open(_os.path.join(_RES_DIR, "strings.yaml"), encoding="UTF-8") as f:
    _CONFIG_YAML = _yaml.safe_load(f)

# Hard code the root section as the yaml file is only used for strings resources
_MAIN_YAML_SECTION = "strings"


class _YAMLStringsGetter(type):
    """
    Implements a custom metaclass used for accessing configuration data by simply accessing class attributes.

    `section` specifies the YAML configuration section (or "key") in which the configuration lives, and must be set.

    Example Usage:

        # strings.yaml
        strings:
            apply_cog:
                new_application: '(...)'
                application_completed: '(...)'

        # strings.py
        class Application(metaclass=YAMLGetter):
            section = "apply_cog"

        # Usage in Python code
        import strings
        print(strings.Application.new_application)
    """

    def __getattr__(cls, name):
        name = name.lower()

        try:
            if cls.section is not None:
                return _CONFIG_YAML[_MAIN_YAML_SECTION][cls.section][name]
            else:
                raise KeyError("Can not access the values without providing a \"section\" key")
        except KeyError:
            dotted_path = '.'.join((cls.section, name))
            _Log.error(f"Tried accessing configuration variable at `{dotted_path}`, but it could not be found.")
            raise

    def __getitem__(cls, name):
        return cls.__getattr__(name)

    def __iter__(cls):
        """
        Return generator of key: value pairs of current constants class' config values.
        """
        for name in cls.__annotations__:
            yield name, getattr(cls, name)


class Application(metaclass=_YAMLStringsGetter):
    """
    Strings related to the member application process (and the application cog).
    """
    section = "apply_cog"
    new_application: str
    completed: str
    check_progress: str
    dm_only: str
    submitted: str
    unfinished: str
    cancelled: str
    not_started: str
    submit: str


class Utils(metaclass=_YAMLStringsGetter):
    """
    Strings related to the utils module.
    """
    section = "utils_module"
    steam_profile_long: str
    steam_profile_short: str
    tw_profile_long: str
    tw_profile_short: str
    country_long: str
    country_short: str
    english_fluency_long: str
    english_fluency_short: str
    dof_first_encounter_long: str
    dof_first_encounter_short: str
    dof_why_join_long: str
    dof_why_join_short: str
    other_games_long: str
    other_games_short: str
    time_availability_long: str
    time_availability_short: str
    anything_else_long: str
    anything_else_short: str


class Info(metaclass=_YAMLStringsGetter):
    """
    Strings related to the general information (and the information cog).
    """
    section = "info_cog"
    welcome: str
    bot_welcome: str
    bot_tutorial: str
    bot_output: str
    bot_browse: str
    rules_welcome: str
    rules_first: str
    rules_second: str
    rules_third: str
    rules_fourth: str
    rules_fifth: str
    rules_sixth: str
    links_welcome: str
    links_ts: str
    links_website: str
    links_public_steam: str
    links_private_steam: str
    authors_welcome: str
    authors_bertalicious: str
    authors_support: str
    authors_link: str


class Help(metaclass=_YAMLStringsGetter):
    """
    Strings related to the help session (and the help cog).
    """
    section = "help_cog"
    invalid_query: str
    help_title: str
    help_aliases: str


class Bl_Characters(metaclass=_YAMLStringsGetter):
    """
    Character strings for bannerlord characters
    """
    section = "bl_character.cog"
    invalid_query: str
    introduction = "Hello! If you wanna receive a certain character code, type in !bl_character [Name] and you'll receive it. The following characters are available:\n" \
                   "Rhagaea\nIra\nElys"