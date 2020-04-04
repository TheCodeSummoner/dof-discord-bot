"""
TODO: Docs
"""
import discord


class MemberApplication:
    """
    TODO: Docs
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
        TODO: Docs
        """
        return self._progress + 1

    @property
    def next_question(self) -> str:
        """
        TODO: Docs
        """
        return MemberApplication.questions[self._progress]

    @property
    def answers(self) -> str:
        """
        TODO: Docs
        """
        return str.join("\n", (f"{MemberApplication._questions_summary[i]}: {self._answers[i]}"
                               for i in range(len(self._answers)))) + "\n"

    @property
    def finished(self) -> bool:
        """
        TODO: Docs
        """
        return self._progress == len(MemberApplication.questions)

    def add_answer(self, answer: str):
        """
        TODO: Docs
        """
        self._progress += 1
        self._answers.append(answer)
