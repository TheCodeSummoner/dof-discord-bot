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
    'subsection' specifies an optional section within the parent section. Use it to access nested values.

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
    section: str
    subsection: str = None

    def __getattr__(cls, name):
        name = name.lower()
        try:
            if cls.subsection is not None:
                return _CONFIG_YAML[_MAIN_YAML_SECTION][cls.section][cls.subsection][name]
            elif cls.section is not None:
                return _CONFIG_YAML[_MAIN_YAML_SECTION][cls.section][name]
            else:
                raise KeyError("Can not access the values without providing a \"section\" key")
        except KeyError:
            dotted_path = ".".join((cls.subsection, cls.section, name) if cls.subsection else (cls.section, name))
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


class General(metaclass=_YAMLStringsGetter):
    """
    Strings related to the most general, discord-related features (e.g. handling channel changes).
    """
    section = "general"
    failed_create_channel: str
    failed_rename_channel: str


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
    authors_white_noise: str
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


class Characters(metaclass=_YAMLStringsGetter):
    """
    Strings related to the character session (and the character cog)
    """
    section = "character_cog"
    title: str
    invalid_character: str
    introduction: str
    explanation: str
    example_success: str
    available_male_characters: str
    available_female_characters: str
    available_custom_characters: str


class FemaleCharacters(metaclass=_YAMLStringsGetter):
    """
    Female Bannerlord character codes.
    """
    section = "character_cog"
    subsection = "female_characters"
    rhagaea: str
    alijin: str
    bolat: str
    yana: str
    abagai: str
    alynneth: str
    wythuin: str
    anat: str
    mesui: str
    alcaea: str
    nywin: str
    asela: str
    silvind: str
    liena: str
    elys: str
    calatild: str
    elthild: str
    philenora: str
    panalea: str
    ira: str
    helea: str
    debana: str
    mina: str
    phaea: str
    sora: str
    chalia: str
    zoana: str
    jathea: str
    martira: str
    rhagaea: str
    lysica: str
    melkea: str
    vendelia: str
    phenoria: str
    zerosica: str
    varra: str
    anidha: str
    arwa: str
    manan: str
    ruma: str
    maraa: str
    jinda: str
    svana: str
    idrun: str
    erta: str
    siga: str
    asta: str


class MaleCharacters(metaclass=_YAMLStringsGetter):
    """
    Male Bannerlord character codes.
    """
    section = "character_cog"
    subsection = "male_characters"
    chaghan: str
    esur: str
    nayantai: str
    temun: str
    bortu: str
    oragur: str
    hurunag: str
    akrum: str
    ilatar: str
    kanujan: str
    taslur: str
    ulman: str
    achaku: str
    kinteg: str
    mehir: str
    muinser: str
    raonul: str
    pryndor: str
    luichan: str
    aeron: str
    aradwyr: str
    branoc: str
    fenagan: str
    siaramus: str
    carfyd: str
    fiarad: str
    monchug: str
    bagai: str
    tulag: str
    khada: str
    suran: str
    bestein: str
    culharn: str
    sein: str
    melidir: str
    ergeon: str
    caladog: str
    ecarand: str
    vartin: str
    peric: str
    lucand: str
    hecard: str
    belgir: str
    servic: str
    ospir: str
    varmund: str
    morcan: str
    elbet: str
    ingalther: str
    erdurand: str
    morcon: str
    morcon: str
    romund: str
    lasand: str
    thomund: str
    furnhard: str
    alary: str
    unthery: str
    aldric: str
    derthert: str
    qahin: str
    hashan: str
    ukhai: str
    karith: str
    talas: str
    awdhan: str
    ghuzid: str
    suruq: str
    iyalas: str
    nuqar: str
    thamza: str
    dhiyul: str
    addas: str
    usair: str
    haqan: str
    tais: str
    adram: str
    tariq: str
    lashonek: str
    galden: str
    alvar: str
    unqid: str
    tovir: str
    svedorn: str
    fafen: str
    vashorki: str
    ratagost: str
    yorig: str
    vyldur: str
    sven: str
    vidar: str
    isvan: str
    lek: str
    simir: str
    mimir: str
    urik: str
    godun: str
    raganvad: str
    olek: str
    sechanis: str
    abalytos: str
    tharos: str
    niphon: str
    ascyron: str
    oros: str
    honoratus: str
    zeno: str
    pharon: str
    maximin: str
    crotor: str
    apys: str
    phadon: str
    garios: str
    penton: str
    manteos: str
    lucon: str
    urkhun: str
    solun: str
    kuyug: str
    undul: str
    nimr: str
    olek_the_old: str
    baranor: str
    serandon: str
    seranor: str
    sejaron: str
    turiados: str
    joron: str
    sichanis: str
    vipon: str
    ovagos: str
    altenos: str
    saratis: str
    achios: str
    tynops: str
    desporion: str
    tasynor: str
    miron: str
    lantanor: str
    olypos: str
    gyphor: str
    nicasor: str
    milos: str
    encurion: str
    chason: str
    nemos: str
    ulbos: str
    obron: str
    belithor: str
    arcor: str
    arion: str
    sanion: str
    eutropius: str
    temion: str
    meritor: str
    patyr: str
    thephilos: str
    eronyx: str
    jastion: str
    tadeos: str
    andros: str


class CustomCharacters(metaclass=_YAMLStringsGetter):
    """
    Custom Bannerlord character codes.
    """
    section = "character_cog"
    subsection = "custom_characters"
    druidess_by_rawex: str
    stannis_baratheon: str
    tyrion_lannister: str
    khal_drogo: str
    sandor_clegane: str
    tywin_lannister: str
    bronn_of_the_blackwater: str
    jon_snow: str
    joffrey_baratheon: str
    tormund_giantsbane: str
    hodor: str
    looter_hero: str
    sea_raiders_hero: str
    mountain_bandits_hero: str
    forest_bandits_hero: str
    desert_bandits_hero: str
    steppe_bandits_hero: str
