"""SynTagRus-based Patterns для улучшенной сегментации русского текста.

Based on:
- SynTagRus corpus (Russian dependency treebank)
- OpenCorpora sentence segmentation rules
- GICRYA and RNC corpora patterns

Optimized for:
- News articles (main use case)
- Literary texts
- Scientific papers
- Formal documents
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from re import Pattern


@dataclass
class SegmentationRule:
    """Rule for sentence segmentation."""

    name: str
    pattern: Pattern[str]
    is_boundary: bool
    priority: int  # Higher priority rules checked first
    description: str


class SynTagRusPatterns:
    """SynTagRus-based patterns для сегментации предложений."""

    # Аббревиатуры, которые НЕ завершают предложение
    ABBREVIATIONS = {
        # Географические
        "г",
        "гг",
        "г-н",
        "г-жа",  # Год, годы, господин, госпожа
        "ул",
        "пр",
        "пл",
        "пер",
        "просп",
        "наб",  # Улица, проспект, площадь...
        "д",
        "дом",
        "корп",
        "стр",
        "кв",  # Дом, корпус, строение, квартира
        "обл",
        "р-н",
        "п",
        "с",
        "дер",
        "пос",  # Область, район, посёлок...
        # Научные степени и звания
        "акад",
        "проф",
        "доц",
        "к",
        "канд",
        "докт",  # Академик, профессор...
        "м",
        "н",
        "мл",
        "ст",  # Младший, старший научный сотрудник
        # Титулы
        "им",
        "ген",
        "полк",
        "подп",
        "лейт",
        "кап",  # Имени, генерал...
        # Временные
        "в",
        "вв",
        "р",
        "руб",
        "коп",  # Век, рубль, копейка
        "ч",
        "час",
        "мин",
        "сек",  # Час, минута, секунда
        # Общие сокращения
        "т",
        "тт",
        "пп",
        "рис",
        "илл",
        "табл",  # Том, пункт, рисунок...
        "см",
        "ср",
        "напр",
        "в т.ч",
        "и т.д",
        "и т.п",
        "и др",  # Смотри, сравни...
        "др",
        "проч",
        "прим",
        "примеч",  # Другое, прочее, примечание
        # Измерения
        "кг",
        "мг",
        "ц",
        "л",  # Килограмм, грамм...
        "мм",
        "км",
        "га",  # Метр, сантиметр...
        "млн",
        "млрд",
        "тыс",
        "трлн",  # Миллион, миллиард...
        # Организационные
        "о-во",
        "о-ва",
        "о-ние",
        "о-ния",  # Общество, общества...
        "зам",
        "пом",
        "зав",
        "нач",  # Министр, заместитель...
        # Прочие
        "etc",
        "et al",
        "ibid",
        "op cit",  # Латинские
        "англ",
        "нем",
        "франц",
        "итал",
        "исп",  # Языки
    }

    # Почетные звания и должности (часто перед ФИО)
    TITLES = {
        "президент",
        "премьер",
        "министр",
        "губернатор",
        "мэр",
        "директор",
        "председатель",
        "генеральный",
        "академик",
        "профессор",
        "доктор",
        "господин",
        "госпожа",
        "товарищ",
    }

    # Слова, после которых часто идет прямая речь
    SPEECH_VERBS = {
        "сказал",
        "сказала",
        "сказали",
        "говорил",
        "говорила",
        "ответил",
        "ответила",
        "спросил",
        "спросила",
        "заявил",
        "заявила",
        "отметил",
        "отметила",
        "подчеркнул",
        "подчеркнула",
        "добавил",
        "добавила",
        "пояснил",
        "пояснила",
        "уточнил",
        "уточнила",
    }

    def __init__(self) -> None:
        """Initialize SynTagRus patterns."""
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficient matching."""

        self.rules: list[SegmentationRule] = [
            # Priority 10: STRONG boundaries
            # Sentence end followed by capital letter
            SegmentationRule(
                name="sentence_end_capital",
                pattern=re.compile(r"[.!?]+\s+(?=[А-ЯЁ«\"\'(])"),
                is_boundary=True,
                priority=50,
                description="Sentence end + capital letter",
            ),
            # Sentence end at paragraph boundary
            SegmentationRule(
                name="paragraph_end",
                pattern=re.compile(r"[.!?]+\s*\n\s*\n"),
                is_boundary=True,
                priority=45,
                description="Sentence end + paragraph break",
            ),
            # Question or exclamation with space
            SegmentationRule(
                name="question_exclamation",
                pattern=re.compile(r"[!?]+\s+"),
                is_boundary=True,
                priority=40,
                description="Question or exclamation mark",
            ),
        ]

        # Additional compiled patterns for quick checks
        self.abbr_pattern = re.compile(
            r"\b(" + "|".join(re.escape(abbr) for abbr in self.ABBREVIATIONS) + r")\."
        )

        self.initials_pattern = re.compile(r"\b[А-ЯЁ]\.\s*(?:[А-ЯЁ]\.\s*)?[А-ЯЁ][а-яё]+\b")

        self.sentence_end_pattern = re.compile(r"[.!?]+\s+[А-ЯЁ«\"\'(]")

    def is_abbreviation(self, text: str, pos: int) -> bool:
        """Проверяет, является ли точка в позиции pos частью аббревиатуры.

        Args:
            text: Text to check
            pos: Position of the dot

        Returns:
            True if dot is part of abbreviation
        """
        if pos <= 0 or pos >= len(text):
            return False

        # Look back for abbreviation
        # Check 1-10 characters before the dot
        for look_back in range(1, min(11, pos + 1)):
            preceding = text[pos - look_back : pos].lower().strip()
            if preceding in self.ABBREVIATIONS:
                return True

        return False

    def is_initials_context(self, text: str, pos: int) -> bool:
        """Проверяет, находится ли точка в контексте инициалов.

        Args:
            text: Text to check
            pos: Position of the dot

        Returns:
            True if in initials context
        """
        # Check surrounding context (±20 chars)
        start = max(0, pos - 20)
        end = min(len(text), pos + 20)
        context = text[start:end]

        return bool(self.initials_pattern.search(context))

    def find_sentence_boundaries(self, text: str) -> list[int]:
        """Находит границы предложений в тексте.

        Args:
            text: Text to segment

        Returns:
            List of boundary positions (indices)
        """
        boundaries = []

        # Apply rules in priority order
        for rule in sorted(self.rules, key=lambda r: r.priority, reverse=True):
            for match in rule.pattern.finditer(text):
                pos = match.end()

                if rule.is_boundary:
                    # Check if not blocked by higher priority rules
                    if not self._is_blocked_boundary(text, pos):
                        boundaries.append(pos)

        # Sort and deduplicate
        boundaries = sorted(set(boundaries))

        return boundaries

    def _is_blocked_boundary(self, text: str, pos: int) -> bool:
        """Проверяет, блокируется ли граница высокоприоритетным правилом.

        Args:
            text: Text
            pos: Boundary position

        Returns:
            True if boundary is blocked
        """
        # Check for abbreviation
        if self.is_abbreviation(text, pos - 1):
            return True

        # Check for initials
        if self.is_initials_context(text, pos):
            return True

        # Check for decimal number
        if pos > 0 and pos < len(text):
            if text[pos - 1].isdigit() and text[pos].isdigit():
                return True

        return False

    def get_quality_score(self, text: str, boundaries: list[int]) -> float:
        """Оценивает качество сегментации.

        Args:
            text: Original text
            boundaries: Found boundaries

        Returns:
            Quality score (0.0 to 1.0)
        """
        if not boundaries:
            return 0.0

        score = 1.0
        penalties = 0

        # Check for common errors
        sentences = self._split_by_boundaries(text, boundaries)

        for sent in sentences:
            sent = sent.strip()

            # Too short sentence (likely error)
            if len(sent) < 3:
                penalties += 0.1

            # Starts with lowercase (likely error)
            if sent and sent[0].islower():
                penalties += 0.15

            # Contains only abbreviation
            if len(sent) < 10 and self.abbr_pattern.search(sent):
                penalties += 0.2

        # Apply penalties
        score = max(0.0, score - penalties)

        return score

    def _split_by_boundaries(self, text: str, boundaries: list[int]) -> list[str]:
        """Splits text by boundaries.

        Args:
            text: Text to split
            boundaries: Boundary positions

        Returns:
            List of sentences
        """
        sentences = []
        start = 0

        for boundary in boundaries:
            sentence = text[start:boundary].strip()
            if sentence:
                sentences.append(sentence)
            start = boundary

        # Last sentence
        if start < len(text):
            sentence = text[start:].strip()
            if sentence:
                sentences.append(sentence)

        return sentences


# Global instance for efficiency
_global_patterns: SynTagRusPatterns | None = None


def get_syntagrus_patterns() -> SynTagRusPatterns:
    """Get global SynTagRus patterns instance.

    Returns:
        SynTagRusPatterns instance
    """
    global _global_patterns

    if _global_patterns is None:
        _global_patterns = SynTagRusPatterns()

    return _global_patterns


__all__ = ["SynTagRusPatterns", "get_syntagrus_patterns", "SegmentationRule"]
