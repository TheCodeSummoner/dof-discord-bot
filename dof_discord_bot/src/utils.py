"""
An unorganised collection of non-static constructs, such as classes or utility functions.
"""
from __future__ import annotations
import os
import abc
import json
import asyncio
import contextlib
import logging
import logging.config
import discord
from discord.ext import commands
from . import strings
from .exceptions import LoggingConfigError
from .constants import DEFAULT_SESSION_ICON, LOG_DIR, LOG_FILE_HANDLERS, LOG_CONFIG_FILE_PATH
from .constants import LAST_PAGE_EMOJI, FIRST_PAGE_EMOJI, NEXT_PAGE_EMOJI, DELETE_EMOJI, PREVIOUS_PAGE_EMOJI


def configure_logging(config_file_path: str = LOG_CONFIG_FILE_PATH, target_log_directory: str = LOG_DIR):
    """
    Configure the built-in logging module using a JSON configuration file.

    All log files will be placed in the "target_log_directory" folder.
    """
    if not os.path.exists(config_file_path):
        raise LoggingConfigError(f"Failed to find the log config file at {config_file_path}")
    if not os.path.exists(target_log_directory):
        raise LoggingConfigError(f"Log directory does not exist at {target_log_directory}")

    try:
        with open(config_file_path, "r") as log_config_file:
            config = json.load(log_config_file)

            # Extract the handlers and update the paths within them to use the correct folder
            handlers = config["handlers"]
            for handler in handlers:
                if handlers[handler]["class"] in LOG_FILE_HANDLERS:
                    handlers[handler]["filename"] = os.path.join(target_log_directory, handlers[handler]["filename"])

    except OSError as exception:
        raise LoggingConfigError("An error occurred while setting configuring logging") from exception

    # Finally, load the configuration
    logging.config.dictConfig(config)


# Initially configure logging and create a log instance referring to the dof bot logger
configure_logging()
Log = logging.getLogger("dof-discord-bot")


class MemberApplication:
    """
    Data storage class containing information about each applicant and their application stage.

    See usage example in `ApplicationCog` (`apply.py`)
    """

    questions = [
        strings.Utils.steam_profile_long,
        strings.Utils.tw_profile_long,
        strings.Utils.country_long,
        strings.Utils.english_fluency_long,
        strings.Utils.dof_first_encounter_long,
        strings.Utils.dof_why_join_long,
        strings.Utils.other_games_long,
        strings.Utils.time_availability_long,
        strings.Utils.anything_else_long
    ]
    questions_summary = [
        strings.Utils.steam_profile_short,
        strings.Utils.tw_profile_short,
        strings.Utils.country_short,
        strings.Utils.english_fluency_short,
        strings.Utils.dof_first_encounter_short,
        strings.Utils.dof_why_join_short,
        strings.Utils.other_games_short,
        strings.Utils.time_availability_short,
        strings.Utils.anything_else_short
    ]

    def __init__(self, member: discord.Member):
        self._member = member
        self._progress = 0
        self._answers = list()

    @property
    def progress(self) -> int:
        """
        Which question is currently being answered (+1 because humans generally don't count from 0).
        """
        return self._progress + 1

    @property
    def question(self) -> str:
        """
        Which question should be answered next.
        """
        return MemberApplication.questions[self._progress]

    @property
    def answers(self) -> str:
        """
        Format and return already provided answers.
        """
        return str.join("\n", (f"{MemberApplication.questions_summary[i]}: {self._answers[i]}"
                               for i in range(len(self._answers)))) + "\n"

    @property
    def finished(self) -> bool:
        """
        Determine whether application should be considered as finished.
        """
        return self._progress == len(MemberApplication.questions)

    def add_answer(self, answer: str):
        """
        Register a new answer and increase the progress counter.
        """
        self._progress += 1
        self._answers.append(answer)


class Page:
    """
    Represent multiple paginator lines, which can be then added all at once.
    """

    def __init__(self, *lines):
        """
        `Lines` can either be a list of strings, or multiple strings which are then packed into a list.

        Keep in mind that an error will be raised if a non-string element is found in either case.
        """
        if len(lines) == 1 and isinstance(lines[0], list):
            lines = lines[0]

        self._lines = list()
        for line in lines:
            if not isinstance(line, str):
                raise TypeError(f"Each page line is expected to be a string, not {type(line)}")
            self._lines.append(line)

    @property
    def lines(self) -> list:
        """
        Getter for the page's lines.
        """
        return self._lines


class LinePaginator(commands.Paginator):
    """
    Restrict the amount of displayed content by checking the number of lines.

    Additionally supports adding a `Page` instance, instead of manually adding each line.
    """

    def __init__(self, max_lines: int = None, **kwargs):
        """
        Max lines argument is used to restrict the maximum amount of content (even though the lines can be as long as \
        needed, as long as they are under the character limit).

        All other keyword-only arguments are passed into the parent constructor.
        """
        super().__init__(**kwargs)
        self.max_lines = max_lines
        self.lines_count = 0

    def add_line(self, line: str = "", *, empty: bool = False):
        """
        Extend add_line method from the parent class - added the functionality to also restrict the number of lines.
        """
        if self.max_lines is not None:
            if self.lines_count >= self.max_lines:
                self.close_page()
            self.lines_count += 1

        super().add_line(line, empty=empty)

    def add_page(self, page: Page):
        """
        Add a `Page` instance (multiple lines at once).
        """
        for line in page.lines:
            self.add_line(line)
        self.close_page()

    def close_page(self):
        """
        Extend close_page method from the parent class - added the functionality to reset line count limiter.

        Note that if the paginator was given the line restriction, the pages may be closed early. Don't pass max_lines
        restriction in the constructor to allow unlimited amount of lines per page.
        """
        self.lines_count = 0
        super().close_page()


class Session:
    """
    Interactive session used to format and display multi-paged text.

    Each session is assigned to the user, and lasts a set amount of time (as specified by timeout), unless refreshed.

    The pages can be browsed using the associated icons on the bottom of the message, or the message (and the session)
    can be terminated early when used with the wastebasket icon.

    When inheriting from this class, you must implement an asynchronous `build_pages` functions, and set the session's
    pages in there.
    """

    def __init__(self, ctx: commands.Context, title: str, icon: str = DEFAULT_SESSION_ICON, timeout: int = 60):
        """
        Create a session given context and the title.

        Keep in mind that this constructor is directly called by the `start` method.

        If you want to pass additional information to the session (for example to build the pages using that
        information), add it to passed context and override init to remember the value.

        Title must be set and will be displayed with the message. Icon is optional and defaults to a question mark.

        Timeout defines after how long of no interaction should the session be ended.
        """
        self.ctx = ctx
        self.bot = ctx.bot
        self.author = ctx.author
        self.destination = ctx.channel
        self.title = title
        self.icon = icon
        self.pages = list()
        self.session_timeout = timeout
        self.current_page = 0
        self.message = None
        self.timeout_task = None

        # Declare a mapping of emoji to reaction functions
        self.reactions = {
            FIRST_PAGE_EMOJI: self.do_first_page,
            PREVIOUS_PAGE_EMOJI: self.do_previous_page,
            NEXT_PAGE_EMOJI: self.do_next_page,
            LAST_PAGE_EMOJI: self.do_last_page,
            DELETE_EMOJI: self.do_delete
        }

    @classmethod
    async def start(cls, ctx: commands.Context, title: str, icon: str = DEFAULT_SESSION_ICON) -> Session:
        """
        Create and begin a session based on the given context.
        """
        Log.info(f"Starting a session, initiated by {ctx.author}")

        session = cls(ctx, title, icon)
        await session.prepare()
        return session

    async def stop(self):
        """
        Stop the session - removes event listeners and attempts to delete the session message.
        """
        Log.info(f"Stopping the session started by {self.author}")

        self.bot.remove_listener(self.on_reaction_add)
        self.bot.remove_listener(self.on_message_delete)

        # Ignore if permission issue, or the message doesn't exist
        with contextlib.suppress(discord.HTTPException, AttributeError):
            await self.message.delete()

    async def prepare(self):
        """
        Set up the (session) pages, events, message, and reactions.
        """
        Log.debug(f"Preparing the session for {self.author}")

        # Create paginated content
        await self.build_pages()

        # Only continue if there are pages to display - otherwise stop the session early
        if self.pages:

            # Setup the listeners to allow page browsing
            self.bot.add_listener(self.on_reaction_add)
            self.bot.add_listener(self.on_message_delete)

            # Display the first page
            await self.update_page()

            # Initial timeout reset to set the timer
            self.reset_timeout()

            # Add the reactions once the message is visible
            self.add_reactions()

        else:
            await self.stop()

    @abc.abstractmethod
    async def build_pages(self):
        """
        To be overridden - each session needs to know how to create the pages.

        You MUST set self.pages in this method to a list of paginator's pages:

            paginator = LinePaginator()
            # Code which adds pages to paginator

            self.pages = paginator.pages
        """

    @property
    def is_first_page(self) -> bool:
        """
        Check if session is currently showing the first page.
        """
        return self.current_page == 0

    @property
    def is_last_page(self) -> bool:
        """
        Check if the session is currently showing the last page.
        """
        return self.current_page == (len(self.pages) - 1)

    async def do_first_page(self):
        """
        Event that is called when the user requests the first page.
        """
        Log.debug(f"Getting first page for {self.author}")

        if not self.is_first_page:
            await self.update_page(0)

    async def do_previous_page(self):
        """
        Event that is called when the user requests the previous page.
        """
        Log.debug(f"Getting previous page for {self.author}")

        if not self.is_first_page:
            await self.update_page(self.current_page - 1)

    async def do_next_page(self):
        """
        Event that is called when the user requests the next page.
        """
        Log.debug(f"Getting next page for {self.author}")

        if not self.is_last_page:
            await self.update_page(self.current_page + 1)

    async def do_last_page(self):
        """
        Event that is called when the user requests the last page.
        """
        Log.debug(f"Getting last page for {self.author}")

        if not self.is_last_page:
            await self.update_page(len(self.pages) - 1)

    async def do_delete(self):
        """
        Event that is called when the user requests to stop the help session.
        """
        Log.debug(f"Deleting the message for {self.author}")

        await self.message.delete()

    async def timeout(self):
        """
        Wait for a set number of seconds, then stop the help session.
        """
        await asyncio.sleep(self.session_timeout)
        await self.stop()

    def reset_timeout(self):
        """
        Cancel the original timeout task and set it up again from the start.

        Used mainly to keep the session after users interact with it.
        """
        Log.debug(f"A user action by {self.author} forced the timeout reset")

        # Cancel the original task if it exists
        if self.timeout_task:
            if not self.timeout_task.cancelled():
                self.timeout_task.cancel()

        # Recreate the timeout task
        self.timeout_task = self.bot.loop.create_task(self.timeout())

    def add_reactions(self):
        """
        Add relevant reactions to the session message, a delete emoji is when pagination is not required.
        """
        Log.debug(f"Adding reactions for {self.author}'s session")

        if len(self.pages) > 1:
            for reaction in self.reactions:
                self.bot.loop.create_task(self.message.add_reaction(reaction))
        else:
            self.bot.loop.create_task(self.message.add_reaction(DELETE_EMOJI))

    async def update_page(self, page_number: int = 0):
        """
        Display the initial page, or change the existing one to the given page number.
        """
        self.current_page = page_number
        embed_page = self.embed_page(page_number)

        if not self.message:
            self.message = await self.destination.send(embed=embed_page)
        else:
            await self.message.edit(embed=embed_page)

    def embed_page(self, page_number: int = 0) -> discord.Embed:
        """
        Return an Embed with the requested page formatted within.
        """
        embed = discord.Embed()

        embed.set_author(name=self.title, icon_url=self.icon)
        embed.description = self.pages[page_number]

        # Add page counter to footer if paginating
        page_count = len(self.pages)
        if page_count > 1:
            embed.set_footer(text=f"Page {self.current_page + 1} / {page_count}")

        return embed

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """
        Event handler for when reactions are added on the session message.
        """
        Log.debug(f"Reaction added by {user.display_name}")

        # Ensure it was the relevant session message
        if reaction.message.id != self.message.id:
            return

        # Ensure it was the session author who reacted
        if user.id != self.author.id:
            return

        # Only handle valid action emoji-s
        if str(reaction.emoji) in self.reactions:
            self.reset_timeout()
            await self.reactions[str(reaction.emoji)]()
        else:
            return

        # Remove the added reaction to prep for re-use
        with contextlib.suppress(discord.HTTPException):
            Log.debug(f"Reaction by {user.display_name} handled by the session")
            await self.message.remove_reaction(reaction, user)

    async def on_message_delete(self, message: discord.Message):
        """
        Close the help session when the session message is deleted.
        """
        if message.id == self.message.id:
            await self.stop()


class MessageEmbed(discord.Embed):
    """
    Shortcut creation of embeds by providing a pre-prepared success/error message embed.
    """

    def __init__(self, message: str, negative: bool = False):
        super().__init__()
        self.title = message
        self.colour = discord.Colour.red() if negative else discord.Colour.green()
