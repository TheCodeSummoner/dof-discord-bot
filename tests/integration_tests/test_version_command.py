"""
Tests associated with the !version command.
"""
import discord
import pytest
import dof_discord_bot
from . import helpers
from dof_discord_bot.src.logger import Log


@helpers.threaded_async
async def test_returns_current_version():
    """
    Simply calling the command should result in bot's current version being printed.
    """
    async def version_to_appear():
        """
        Make sure that the bot answers the command and current version is returned.
        """
        message = helpers.get_test_channel().last_message

        if message and message.author.name == "DofDevBotApplication":
            assert message.embeds[0].title == f"{dof_discord_bot.__title__} v{dof_discord_bot.__version__}"
            return True

        Log.debug("Waiting for the response to the !version command to appear")

    def or_fail():
        """
        Otherwise, fail the test.
        """
        pytest.fail("Timed out waiting for response to the !version command")

    await helpers.get_test_channel().send("!version")
    await helpers.wait_for(version_to_appear, or_fail)


@helpers.threaded_async
async def test_returns_error_on_missing_role():
    """
    TODO: Tom to add documentation

    TODO: Tests' README.md should mention that before running the code you should make sure dof tester bot has the defender role
    """
    async def error_to_appear():
        """
        Calling the command without a Defender role should result in the error message being printed.
        """
        # TODO: Write code ;)
        pass

    def or_fail():
        """
        Otherwise, fail the test.
        """
        pytest.fail("Timed out waiting for response to the !version command")

    def get_tester_bot_member() -> discord.Member:
        """
        Helper command to retrieve the testing bot using the unique identifier.
        """
        for member in helpers.dof_bot.get_all_members():
            if member.id == 720954603046305855:
                return member

    tester_bot_member = get_tester_bot_member()
    defender_role = discord.utils.get(helpers.dof_bot.guild.roles, name="test")  # TODO: Change this to use the "Defneder" role in the final code
    await tester_bot_member.remove_roles(defender_role)
    await helpers.get_test_channel().send("!version")
    await helpers.wait_for(error_to_appear, or_fail)
    await tester_bot_member.add_roles(defender_role)
