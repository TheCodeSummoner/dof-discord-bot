"""
An unorganised collection of non-static constructs, such as classes or utility functions.
"""
import discord


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
        "What is your Steam profile link?",
        "What is your TaleWorlds profile link (if you have one)?",
        "Which country are you from?",
        "How well can you speak English?",
        "How did you find out about DoF?",
        "Why would you like to become a Defender?",
        "What other games do you play?",
        "When can you usually play (BST zone for EUs and EST for NAs)?",
        "Anything you would like to add (type \"No\" if nothing to add)?"
    ]
    _questions_summary = [
        "Steam profile",
        "TaleWorlds profile",
        "Country",
        "English fluency",
        "How did you find out about DoF",
        "Why would you like to become a Defender",
        "Other games",
        "Time availability",
        "Other"
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
