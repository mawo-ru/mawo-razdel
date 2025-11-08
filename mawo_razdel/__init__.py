"""MAWO RAZDEL - Enhanced Russian Tokenization
Upgraded tokenization with 100% compatibility with original razdel.

Features:
- Full backward compatibility with razdel API
- All original razdel features preserved
- Additional SynTagRus patterns available
- Abbreviation handling (г., ул., им., т.д.)
- Initials support (А. С. Пушкин)
- Direct speech patterns
"""

from __future__ import annotations

# Import original razdel implementation (ported)
from .segmenters import sentenize as _original_sentenize
from .segmenters import tokenize as _original_tokenize

# Import classes from substring module
from .substring import Substring


# Backwards compatibility aliases
class Token:
    """Token with position information."""

    def __init__(self, text: str, start: int, stop: int) -> None:
        self.text = text
        self.start = start
        self.stop = stop

    def __repr__(self) -> str:
        return f"Token('{self.text}', {self.start}, {self.stop})"


class Sentence:
    """Sentence with text."""

    def __init__(self, text: str, start: int = 0, stop: int = 0) -> None:
        self.text = text
        self.start = start
        self.stop = stop

    def __repr__(self) -> str:
        return (
            f"Sentence('{self.text[:30]}...')"
            if len(self.text) > 30
            else f"Sentence('{self.text}')"
        )


# Main API functions - use original razdel implementation
def tokenize(text: str):
    """Tokenize Russian text using original razdel algorithm.

    Returns an iterator of Substring objects.

    Examples:
        >>> list(tokenize('что-то'))
        [Substring(0, 6, 'что-то')]

        >>> list(tokenize('1,5'))
        [Substring(0, 3, '1,5')]
    """
    return _original_tokenize(text)


def sentenize(text: str):
    """Segment Russian text into sentences using original razdel algorithm.

    Returns an iterator of Substring objects.

    Examples:
        >>> list(sentenize('Привет. Как дела?'))
        [Substring(0, 7, 'Привет.'), Substring(8, 17, 'Как дела?')]

        >>> list(sentenize('А. С. Пушкин родился в 1799 г.'))
        [Substring(0, 31, 'А. С. Пушкин родился в 1799 г.')]
    """
    return _original_sentenize(text)


__version__ = "1.0.2"
__author__ = "MAWO Team (based on Razdel by Alexander Kukushkin)"

__all__ = [
    "tokenize",
    "sentenize",
    "Token",
    "Sentence",
    "Substring",
]
