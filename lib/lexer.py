from collections import deque
from shlex import shlex
from typing import Optional


class Lexer:
    def __init__(self, text):
        self.lexer = shlex(text, posix=True)
        self.lexer.commenters = ""
        self.lexer.wordchars += "-"
        self.tokens = deque(self.lexer)
        self.spent_tokens = deque()

    def next(self) -> Optional[str]:
        if len(self.tokens) == 0:
            return None
        token = self.tokens.popleft()
        self.spent_tokens.append(token)
        return token
