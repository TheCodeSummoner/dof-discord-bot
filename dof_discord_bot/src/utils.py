"""
An unorganised collection of non-static constructs, such as classes or utility functions.
"""
import discord as _discord
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
