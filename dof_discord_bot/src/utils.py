"""
An unorganised collection of non-static constructs, such as classes or utility functions.
"""
import discord as _discord
from discord.ext import commands as _commands
from . import strings as _strings


class MemberApplication:
    """
    Member application class storing information about each applicant and the application stage.

    Functions
    ---------

    The following list shortly summarises each function:

        * progress - get application progress
        * question - get current question
        * answers - get current answers
        * finished - is the application finished
        * add_answer - register a new answer

    See usage example in `ApplicationCog` (*apply.py*)
    """
    questions = [
        _strings.Utils.steam_profile_long,
        _strings.Utils.tw_profile_long,
        _strings.Utils.country_long,
        _strings.Utils.english_fluency_long,
        _strings.Utils.dof_first_encounter_long,
        _strings.Utils.dof_why_join_long,
        _strings.Utils.other_games_long,
        _strings.Utils.time_availability_long,
        _strings.Utils.anything_else_long
    ]
    _questions_summary = [
        _strings.Utils.steam_profile_short,
        _strings.Utils.tw_profile_short,
        _strings.Utils.country_short,
        _strings.Utils.english_fluency_short,
        _strings.Utils.dof_first_encounter_short,
        _strings.Utils.dof_why_join_short,
        _strings.Utils.other_games_short,
        _strings.Utils.time_availability_short,
        _strings.Utils.anything_else_short
    ]

    def __init__(self, member: _discord.Member):
        self._member = member
        self._progress = 0
        self._answers = list()

    @property
    def progress(self) -> int:
        """
        Getter for which question is currently being answered (+1 because humans generally don't count from 0)
        """
        return self._progress + 1

    @property
    def question(self) -> str:
        """
        Getter for current question.
        """
        return MemberApplication.questions[self._progress]

    @property
    def answers(self) -> str:
        """
        Get formatted answers.
        """
        return str.join("\n", (f"{MemberApplication._questions_summary[i]}: {self._answers[i]}"
                               for i in range(len(self._answers)))) + "\n"

    @property
    def finished(self) -> bool:
        """
        Get boolean determining whether application should be considered finished.
        """
        return self._progress == len(MemberApplication.questions)

    def add_answer(self, answer: str):
        """
        Function used to register a new answer and increase the progress counter.
        """
        self._progress += 1
        self._answers.append(answer)


class Page:
    """
    Page class is used to represent multiple paginator lines, which can be then added all at once.
    """

    def __init__(self, *lines):
        """
        `Lines` can either be a list of strings, or multiple strings which are then packed into a list.

        Keep in mind that a value error will be thrown if a non-string element is found in either case.
        """
        if len(lines) == 1 and isinstance(lines[0], list):
            lines = lines[0]

        self._lines = list()
        for line in lines:
            if not isinstance(line, str):
                raise ValueError(f"Each page line is expected to be a string, not {type(line)}")
            self._lines.append(line)

    @property
    def lines(self):
        """
        Getter for the page lines.
        """
        return self._lines


class LinePaginator(_commands.Paginator):
    """
    Extended paginator used to restrict the amount of displayed content by checking the number of lines.

    Additionally supports adding a `Page` instance, instead of manually adding each line.
    """

    def __init__(self, max_lines: int = None, **kwargs):
        """
        Max lines argument is used to restrict the maximum amount of content (even though the lines can be as long as
        needed, as long as they are under the character limit).

        All other keyword-only arguments are passed into the parent constructor.
        """
        super().__init__(**kwargs)
        self.max_lines = max_lines
        self.lines_count = 0

    def add_line(self, line: str = "", *args, **kwargs):
        """
        Extended add_line method from the parent class, added the functionality to also restrict the number of lines.
        """
        if self.max_lines is not None:
            if self.lines_count >= self.max_lines:
                self.close_page()
            self.lines_count += 1

        super().add_line(line, *args, **kwargs)

    def add_page(self, page: Page):
        """
        New support method to allow adding multiple lines (pages) at once.
        """
        for line in page.lines:
            self.add_line(line)
        self.close_page()

    def close_page(self):
        """
        Extended close_page method from the parent class, added the functionality to reset line count limiter.

        Note that if the paginator was given the line restriction, the pages may be closed early. Don't pass max_lines
        restriction in the constructor to allow unlimited amount of lines per page.
        """
        self.lines_count = 0
        super().close_page()
