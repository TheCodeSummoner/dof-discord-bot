"""
An unorganised collection of non-static constructs, such as classes or utility functions.
"""
import discord
from . import strings


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
        strings.STEAM_PROFILE_LONG,
        strings.TW_PROFILE_LONG,
        strings.COUNTRY_LONG,
        strings.ENGLISH_FLUENCY_LONG,
        strings.DOF_FIRST_ENCOUNTER_LONG,
        strings.DOF_WHY_JOIN_LONG,
        strings.OTHER_GAMES_LONG,
        strings.TIME_AVAILABILITY_LONG,
        strings.ANYTHING_ELSE_LONG
    ]
    _questions_summary = [
        strings.STEAM_PROFILE_SHORT,
        strings.TW_PROFILE_SHORT,
        strings.COUNTRY_SHORT,
        strings.ENGLISH_FLUENCY_SHORT,
        strings.DOF_FIRST_ENCOUNTER_SHORT,
        strings.DOF_WHY_JOIN_SHORT,
        strings.OTHER_GAMES_SHORT,
        strings.TIME_AVAILABILITY_SHORT,
        strings.ANYTHING_ELSE_SHORT
    ]

    def __init__(self, member: discord.Member):
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
