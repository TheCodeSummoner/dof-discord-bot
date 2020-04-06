"""
Formattable strings
"""

# Apply cog
NEW_MEMBER_APPLICATION = """Thank you for being interested in joining DoF, {} :)
Please answer each question to submit an application (don't worry, you will have a chance to review your application before submission).
You can cancel your application at any time by typing \"!cancel\".
You can check your application progress at any time by typing \"!apply\"."""
MEMBER_APPLICATION_COMPLETED = """You have completed the application - here is what you've written:
{}
Would you like to submit this application? Type !submit to submit it, or !cancel to cancel the application."""
CHECK_APPLICATION_PROGRESS = """You are currently on step {} out of {}.
Current question is: {}"""
NOT_APPLICATION_DM = """Hi! I've' noticed you've tried to use the {} command, but it can only be used as a direct message.
If you would like to {} a DoF application, please type the command again here."""
APPLICATION_SUBMITTED = """Application from {} successfully submitted."""
APPLICATION_UNFINISHED = """Couldn't find a finished application from {} - please check you have completed an application by using the \"!apply\" command."""
APPLICATION_CANCELLED = """Application from {} successfully cancelled"""
APPLICATION_NOT_STARTED = """Couldn't find a started application from {} - please make sure you have started an application by using the \"!apply\" command"""
SUBMIT_APPLICATION = """New application from {}:

{}"""
