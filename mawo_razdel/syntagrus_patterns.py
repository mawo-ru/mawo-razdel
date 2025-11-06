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

    # Головные аббревиатуры (HEAD) - идут ПЕРЕД именами/названиями
    # После них может быть заглавная буква, но это не начало предложения
    HEAD_ABBREVIATIONS = {
        # Географические (перед названиями)
        "ул",
        "пр",
        "пл",
        "пер",
        "просп",
        "наб",  # улица Тверская
        "г",
        "гор",  # г. Москва (город, не год!)
        "обл",
        "р-н",
        "п",
        "с",
        "дер",
        "пос",  # область, район...
        "им",  # им. Пушкина
        # Титулы и звания (перед именами)
        "г-н",
        "г-жа",
        "гн",
        "госп",  # господин Иванов
        "проф",
        "акад",
        "доц",  # профессор Петров
        "св",  # св. Иоанн
        "ген",
        "полк",
        "подп",
        "лейт",
        "кап",  # генерал Иванов
    }

    # Хвостовые аббревиатуры (TAIL) - идут ПОСЛЕ чисел/слов
    # После них НЕ должно быть заглавной буквы (иначе новое предложение)
    TAIL_ABBREVIATIONS = {
        # Года и века (после чисел)
        "г",
        "гг",
        "в",
        "вв",
        "р",  # 1799 г., XXI в., 250 г. до Р. Х.
        # Адресные (после чисел)
        "д",
        "дом",
        "корп",
        "стр",
        "кв",  # д. 1, стр. 5
        # Временные
        "ч",
        "час",
        "мин",
        "сек",  # 10 ч. 30 мин.
        # Деньги и измерения (после чисел)
        "руб",
        "коп",
        "тыс",
        "млн",
        "млрд",
        "трлн",
        "кг",
        "мг",
        "ц",
        "л",
        "мм",
        "км",
        "га",
        "м",
        # Страницы, тома (после чисел)
        "т",
        "тт",
        "с",
        "пп",
        "рис",
        "илл",
        "табл",  # стр уже в адресных
        # Научные степени (инициалы перед)
        "к",
        "канд",
        "докт",
        "н",  # к.т.н., д.ф.н.
        # Общие (обычно внутри текста или в конце)
        "см",
        "ср",
        "напр",
        "др",
        "проч",
        "прим",
        "примеч",
        "т.е",
        "т.д",
        "т.п",
        "т.к",  # и т.д., и т.п.
        # Организационные
        "о-во",
        "о-ва",
        "о-ние",
        "о-ния",
        "зам",
        "пом",
        "зав",
        "нач",
        # Прочие
        "etc",
        "et al",
        "ibid",
        "op cit",
        "англ",
        "нем",
        "франц",
        "итал",
        "исп",
        "лат",  # Языки
    }

    # Объединенный список всех аббревиатур
    ABBREVIATIONS = HEAD_ABBREVIATIONS | TAIL_ABBREVIATIONS

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
        """Проверяет, является ли точка перед позицией pos частью аббревиатуры.

        Улучшено с проверкой контекста - на основе современных практик NLP (2024-2025).
        Проверяет ПЕРЕД и ПОСЛЕ точки, чтобы определить, действительно ли это аббревиатура,
        которая должна блокировать границу предложения.

        Args:
            text: Текст для проверки
            pos: Позиция ПОСЛЕ точки (граница)

        Returns:
            True если точка - часть аббревиатуры, блокирующей границу предложения
        """
        if pos <= 1 or pos > len(text):
            return False

        # Проверяем, что перед pos действительно точка
        if text[pos - 1] != ".":
            return False

        # Ищем токен аббревиатуры ПЕРЕД точкой
        # Извлекаем слово/токен перед точкой
        before_match = re.search(r"(\w+)\.?$", text[: pos - 1])
        if not before_match:
            return False

        preceding = before_match.group(1).lower()

        # Проверяем, есть ли в нашем списке аббревиатур
        if preceding not in self.ABBREVIATIONS:
            return False

        # КРИТИЧНО: Проверяем что идет ПОСЛЕ точки
        # Это ключевое улучшение на основе современных практик NLP
        remaining = text[pos:].lstrip()

        if not remaining:
            # Конец текста - аббревиатура в конце
            return True

        # Проверяем первый символ после пробелов
        next_char = remaining[0]

        # УЛУЧШЕНИЕ: Различаем HEAD и TAIL аббревиатуры
        is_head = preceding in self.HEAD_ABBREVIATIONS
        is_tail = preceding in self.TAIL_ABBREVIATIONS

        # Если следующий символ - заглавная буква (не цифра)
        if next_char.isupper() and next_char.isalpha():
            # HEAD аббревиатуры (ул., г., проф.) могут идти перед заглавной буквой
            # Например: "ул. Тверская", "г. Москва", "проф. Иванов"
            if is_head:
                return True  # Не разбиваем

            # TAIL аббревиатуры (г., в., д.) НЕ должны идти перед заглавной буквой
            # Исключение: инициалы (А. С. Пушкин)
            if is_tail:
                # Проверяем инициалы: один символ + точка
                if len(remaining) > 2 and remaining[1] == ".":
                    return True  # Часть последовательности инициалов
                # Иначе это начало нового предложения
                return False

        # Строчная буква, цифра или пунктуация после аббревиатуры - оставляем соединенными
        return True

    def is_initials_context(self, text: str, pos: int) -> bool:
        """Проверяет, находится ли точка непосредственно в контексте инициалов.

        Улучшено: проверяем только если инициалы находятся РЯДОМ с границей,
        а не в радиусе 20 символов.

        Args:
            text: Текст для проверки
            pos: Позиция после точки

        Returns:
            True если в непосредственном контексте инициалов
        """
        # Проверяем небольшой контекст: 5 символов до и 10 после
        # Это достаточно для "А. С. Пушкин" но не захватывает далекие инициалы
        start = max(0, pos - 5)
        end = min(len(text), pos + 10)
        context = text[start:end]

        # Дополнительно: точка должна быть ВНУТРИ найденного паттерна инициалов
        match = self.initials_pattern.search(context)
        if not match:
            return False

        # Проверяем, что граница (pos) находится внутри найденного паттерна инициалов
        # или сразу после него (с учетом смещения start)
        match_start = start + match.start()
        match_end = start + match.end()

        # Граница должна быть внутри паттерна или максимум на 2 символа после
        if match_start <= pos <= match_end + 2:
            return True

        return False

    def find_sentence_boundaries(self, text: str) -> list[int]:
        """Находит границы предложений в тексте.

        Args:
            text: Text to segment

        Returns:
            List of boundary positions (indices)
        """
        boundaries = []

        # Find all potential sentence endings
        for match in re.finditer(r"[.!?]+", text):
            pos = match.end()

            # Skip if at end of text
            if pos >= len(text):
                continue

            # Check what comes after
            remaining = text[pos:]

            # Check if this is a valid boundary
            is_valid_boundary = False

            # Case 1: Followed by whitespace and capital letter (русская ИЛИ латинская)
            # УЛУЧШЕНИЕ: добавлена поддержка латинских заглавных (для XXI, IV, и т.д.)
            if re.match(r"\s+[А-ЯЁA-Z«\"\'(]", remaining):
                is_valid_boundary = True

            # Case 2: Followed by paragraph break
            elif re.match(r"\s*\n\s*\n", remaining):
                is_valid_boundary = True

            # Case 3: Question or exclamation (even without capital)
            elif match.group() in ["!", "?", "!!", "??", "!?", "?!"]:
                if re.match(r"\s+", remaining):
                    is_valid_boundary = True

            # Check if boundary is blocked by high-priority rules
            if is_valid_boundary and not self._is_blocked_boundary(text, pos):
                boundaries.append(pos)

        # Sort and deduplicate
        boundaries = sorted(set(boundaries))

        return boundaries

    def _is_blocked_boundary(self, text: str, pos: int) -> bool:
        """Проверяет, блокируется ли граница высокоприоритетным правилом.

        Args:
            text: Текст
            pos: Позиция границы (после точки/знака)

        Returns:
            True если граница блокирована
        """
        # Проверка на аббревиатуру (точка после аббревиатуры)
        # ВАЖНО: is_abbreviation уже проверяет контекст до И после точки
        if pos > 0 and text[pos - 1] == ".":
            # Передаем позицию ПОСЛЕ точки (pos), а не позицию точки
            if self.is_abbreviation(text, pos):
                return True

        # Проверка на инициалы (А. С. Пушкин)
        if self.is_initials_context(text, pos):
            return True

        # Check for decimal number (3.14)
        if pos > 1 and pos < len(text):
            before_char = text[pos - 2] if pos >= 2 else ""
            dot_char = text[pos - 1]
            after_char = text[pos] if pos < len(text) else ""

            # Decimal number pattern: digit + . + digit
            if before_char.isdigit() and dot_char == "." and after_char.isdigit():
                return True

        # Check for ellipsis (...)
        if pos >= 3:
            if text[pos - 3 : pos] == "...":
                return True

        # Check for direct speech continuation: - сказал он. -
        if pos > 10:
            context = text[max(0, pos - 30) : min(len(text), pos + 10)]
            for verb in self.SPEECH_VERBS:
                if verb in context.lower():
                    # Check for pattern: . - word
                    if pos < len(text) - 3:
                        after = text[pos : pos + 3]
                        if after.strip().startswith("-") or after.strip().startswith("—"):
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
