"""
Collection of bot-related exceptions.
"""
import discord


class DofDiscordBotError(discord.DiscordException):
    """
    Base exception for all non-standard errors raised in the application.
    """


class LoggingConfigError(DofDiscordBotError):
    """
    Logging configuration error caused by a misformatted or missing files or directories.
    """


class BannerlordCharacterNotFound(DofDiscordBotError):
    """
    Raised when the character-fetching query doesn't match any of the supported characters.
    """


class HelpQueryNotFound(DofDiscordBotError):
    """
    Raised when a HelpSession query doesn't match a command or a cog.
    """
