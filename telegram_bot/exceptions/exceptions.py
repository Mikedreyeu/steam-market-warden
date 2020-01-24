from emoji import emojize


class CommandException(Exception):
    def __init__(self, message):
        self.message = emojize(f':no_entry_sign: {message}', use_aliases=True)
