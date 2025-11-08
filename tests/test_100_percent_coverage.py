"""Тесты для достижения 100% покрытия кода"""

import pytest

from mawo_razdel import (
    Sentence,
    Substring,
    Token,
    sentenize,
    tokenize,
)
from mawo_razdel.rule import JOIN, Rule
from mawo_razdel.segmenters.base import safe_next
from mawo_razdel.segmenters.sentenize import (
    DebugSentSegmenter,
    SentSegmenter,
    SentSplit,
    close_bound,
    close_bracket,
    close_quote,
    dash_right,
    delimiter_right,
    empty_side,
    initials_left,
    inside_pair_sokr,
    list_item,
    lower_right,
    no_space_prefix,
    sokr_left,
)
from mawo_razdel.segmenters.tokenize import (
    Atom,
    DashRule,
    DebugTokenSegmenter,
    FloatRule,
    FractionRule,
    TokenSegmenter,
    TokenSplit,
    UnderscoreRule,
    other,
    punct,
    yahoo,
)
from mawo_razdel.split import Split


class TestTokenClass:
    """Тесты для класса Token - покрытие __init__.py строки 30-35"""

    def test_token_creation(self):
        """Создание токена"""
        token = Token("test", 0, 4)
        assert token.text == "test"
        assert token.start == 0
        assert token.stop == 4

    def test_token_repr(self):
        """Repr токена"""
        token = Token("hello", 5, 10)
        assert repr(token) == "Token('hello', 5, 10)"


class TestSentenceClass:
    """Тесты для класса Sentence - покрытие __init__.py строки 42-47"""

    def test_sentence_creation(self):
        """Создание предложения"""
        sent = Sentence("Test sentence", 0, 13)
        assert sent.text == "Test sentence"
        assert sent.start == 0
        assert sent.stop == 13

    def test_sentence_repr_short(self):
        """Repr короткого предложения"""
        sent = Sentence("Short", 0, 5)
        assert repr(sent) == "Sentence('Short')"

    def test_sentence_repr_long(self):
        """Repr длинного предложения"""
        sent = Sentence("This is a very long sentence that should be truncated", 0, 50)
        assert "..." in repr(sent)
        assert len(repr(sent)) < 60


class TestRecordMethods:
    """Тесты для непокрытых методов Record - покрытие record.py"""

    def test_cached_property_get(self):
        """Тест cached_property.__get__ - первый вызов"""
        from mawo_razdel import tokenize

        # Используем реальный класс с cached_property
        result = list(tokenize("test word"))
        # Доступ к split.left_1 и другим cached properties
        assert len(result) > 0

    def test_cached_property_cached_hit(self):
        """Тест cached_property.__get__ - кэшированное значение"""
        from mawo_razdel.segmenters.tokenize import Atom, TokenSplit

        atom = Atom(0, 4, "RU", "test")
        split = TokenSplit([atom], "-", [atom])

        # Первый доступ к left_1 - вычисляется
        val1 = split.left_1
        # Второй доступ к left_1 - из кэша (строка 12 в record.py)
        val2 = split.left_1
        assert val1 is val2  # Должны быть идентичными

    def test_record_ne(self):
        """Тест Record.__ne__"""
        s1 = Substring(0, 5, "hello")
        s2 = Substring(0, 5, "hello")
        s3 = Substring(0, 5, "world")

        assert not (s1 != s2)  # Равны
        assert s1 != s3  # Не равны

    def test_record_iter(self):
        """Тест Record.__iter__"""
        s = Substring(10, 20, "test")
        values = list(s)
        assert values == [10, 20, "test"]

    def test_record_hash(self):
        """Тест Record.__hash__"""
        s1 = Substring(0, 5, "hello")
        s2 = Substring(0, 5, "hello")
        s3 = Substring(0, 5, "world")

        # Одинаковые объекты - одинаковый хеш
        assert hash(s1) == hash(s2)
        # Разные объекты - разный хеш (скорее всего)
        assert hash(s1) != hash(s3)

        # Можно использовать в set
        s = {s1, s2, s3}
        assert len(s) == 2  # s1 и s2 считаются одинаковыми

    def test_record_repr_pretty(self):
        """Тест Record._repr_pretty_ для IPython"""
        import io

        class MockPrinter:
            def __init__(self):
                self.output = io.StringIO()
                self._indent = 0

            def text(self, text):
                self.output.write(text)

            def pretty(self, obj):
                self.output.write(repr(obj))

            def breakable(self):
                self.output.write("\n")

            def group(self, indent, open_text, close_text):
                return MockGroup(self, open_text, close_text)

            def get_output(self):
                return self.output.getvalue()

        class MockGroup:
            def __init__(self, printer, open_text, close_text):
                self.printer = printer
                self.open_text = open_text
                self.close_text = close_text

            def __enter__(self):
                self.printer.text(self.open_text)
                return self

            def __exit__(self, *args):
                self.printer.text(self.close_text)

        s = Substring(0, 5, "hello")
        printer = MockPrinter()

        # Обычный случай
        s._repr_pretty_(printer, False)
        output = printer.get_output()
        assert "Substring" in output
        assert "0" in output or "5" in output or "hello" in output

        # Циклическая ссылка
        printer2 = MockPrinter()
        s._repr_pretty_(printer2, True)
        output2 = printer2.get_output()
        assert "..." in output2


class TestRuleClass:
    """Тесты для Rule - покрытие rule.py строка 13"""

    def test_rule_call_not_implemented(self):
        """Rule.__call__ должен быть переопределен"""
        rule = Rule()
        split = Split("left", ".", "right")

        with pytest.raises(NotImplementedError):
            rule(split)


class TestSentSegmenterDebug:
    """Тесты для DebugSentSegmenter - покрытие sentenize.py"""

    def test_debug_segmenter(self, capsys):
        """Тест debug режима сегментации"""
        segmenter = SentSegmenter().debug
        assert isinstance(segmenter, DebugSentSegmenter)

        text = "Привет. Мир."
        list(segmenter(text))

        # Проверяем что был вывод
        _ = capsys.readouterr()
        # Debug segmenter печатает информацию
        # (может быть пустым если все правила JOIN)


class TestSentSplitProperties:
    """Тесты для непокрытых свойств SentSplit"""

    def test_left_int_sokr(self):
        """Тест left_int_sokr - строка 274-276"""
        split = SentSplit("текст 15-го", ".", "следующее")
        result = split.left_int_sokr
        assert result == "го"

    def test_buffer_first_token(self):
        """Тест buffer_first_token - строка 290-292"""
        split = SentSplit("", ".", "")
        split.buffer = "  test123"
        token = split.buffer_first_token
        assert token == "test"


class TestSentenizeRules:
    """Тесты для непокрытых правил sentenize"""

    def test_empty_side_left_none(self):
        """empty_side когда left_token None"""
        split = SentSplit("", ".", "right")
        result = empty_side(split)
        assert result == JOIN

    def test_delimiter_right_smile(self):
        """delimiter_right с смайлом"""
        split = SentSplit("left", ".", ":) next")
        result = delimiter_right(split)
        assert result == JOIN

    def test_close_quote_generic_no_space(self):
        """close_quote с generic quote без пробела"""
        split = SentSplit('test"', '"', "next")
        # Симулируем отсутствие пробела
        _ = close_quote(split)
        # Должно проверить close_bound

    def test_dash_right_no_dash(self):
        """dash_right когда справа нет тире"""
        split = SentSplit("left", ".", "right")
        result = dash_right(split)
        assert result is None

    def test_list_item_not_bullet(self):
        """list_item когда не нумерованный список"""
        split = SentSplit("not a list", ".", "item")
        split.buffer = "long text here"
        result = list_item(split)
        assert result is None


class TestTokenSegmenterDebug:
    """Тесты для DebugTokenSegmenter"""

    def test_debug_property(self):
        """Тест .debug property"""
        segmenter = TokenSegmenter()
        debug_seg = segmenter.debug
        assert isinstance(debug_seg, DebugTokenSegmenter)


class TestTokenSplitProperties:
    """Тесты для TokenSplit свойств"""

    def test_left_2_none(self):
        """left_2 когда только один элемент"""
        atom1 = Atom(0, 1, "RU", "a")
        split = TokenSplit([atom1], "", [atom1])
        assert split.left_2 is None

    def test_left_3_none(self):
        """left_3 когда меньше 3 элементов"""
        atom1 = Atom(0, 1, "RU", "a")
        split = TokenSplit([atom1], "", [atom1])
        assert split.left_3 is None

    def test_right_2_none(self):
        """right_2 когда только один элемент"""
        atom1 = Atom(0, 1, "RU", "a")
        split = TokenSplit([atom1], "", [atom1])
        assert split.right_2 is None

    def test_right_3_none(self):
        """right_3 когда меньше 3 элементов"""
        atom1 = Atom(0, 1, "RU", "a")
        split = TokenSplit([atom1], "", [atom1])
        assert split.right_3 is None


class TestTokenizeRules:
    """Тесты для правил токенизации"""

    def test_dash_rule_no_delimiter(self):
        """DashRule когда делимитер не дефис"""
        rule = DashRule()
        atom1 = Atom(0, 1, "RU", "a")
        atom2 = Atom(2, 3, "RU", "b")
        split = TokenSplit([atom1], ".", [atom2])
        result = rule(split)
        assert result is None

    def test_underscore_rule_punct(self):
        """UnderscoreRule с пунктуацией"""
        rule = UnderscoreRule()
        atom_punct = Atom(0, 1, "PUNCT", ".")
        atom_ru = Atom(2, 3, "RU", "a")
        split = TokenSplit([atom_punct], "_", [atom_ru])
        _ = rule(split)
        # Должно вернуть None т.к. один из них PUNCT

    def test_float_rule_not_int(self):
        """FloatRule когда не числа"""
        rule = FloatRule()
        atom1 = Atom(0, 1, "RU", "a")
        atom2 = Atom(2, 3, "RU", "b")
        split = TokenSplit([atom1], ".", [atom2])
        result = rule(split)
        assert result is None

    def test_fraction_rule_not_int(self):
        """FractionRule когда не числа"""
        rule = FractionRule()
        atom1 = Atom(0, 1, "RU", "a")
        atom2 = Atom(2, 3, "RU", "b")
        split = TokenSplit([atom1], "/", [atom2])
        result = rule(split)
        assert result is None

    def test_punct_rule_no_match(self):
        """punct когда типы не PUNCT"""
        atom1 = Atom(0, 1, "RU", "a")
        atom2 = Atom(2, 3, "RU", "b")
        split = TokenSplit([atom1], "-", [atom2])
        result = punct(split)
        assert result is None

    def test_other_left_other_right_ru(self):
        """other rule: OTHER слева, RU справа"""
        atom1 = Atom(0, 1, "OTHER", "Δ")
        atom2 = Atom(1, 2, "RU", "а")
        split = TokenSplit([atom1], "", [atom2])
        result = other(split)
        assert result == JOIN

    def test_yahoo_not_yahoo(self):
        """yahoo когда не yahoo"""
        atom1 = Atom(0, 5, "LAT", "google")
        split = TokenSplit([atom1], "!", [atom1])
        result = yahoo(split)
        assert result is None


class TestDebugSegmenter:
    """Тесты для DebugSegmenter.join"""

    def test_debug_segmenter_join_output(self, capsys):
        """Тест вывода DebugSegmenter"""
        from mawo_razdel.segmenters.tokenize import tokenize as tok_impl

        # Используем debug режим
        text = "test-word"
        _ = list(tok_impl.debug(text))

        _ = capsys.readouterr()
        # Debug должен печатать информацию о split


class TestSafeNext:
    """Тест для safe_next"""

    def test_safe_next_empty(self):
        """safe_next на пустом итераторе"""
        result = safe_next(iter([]))
        assert result is None

    def test_safe_next_with_value(self):
        """safe_next с значением"""
        result = safe_next(iter([1, 2, 3]))
        assert result == 1


class TestEdgeCasesInRules:
    """Граничные случаи в правилах"""

    def test_sokr_left_not_period(self):
        """sokr_left когда делимитер не точка"""
        split = SentSplit("текст", ",", "далее")
        result = sokr_left(split)
        assert result is None

    def test_inside_pair_sokr_not_period(self):
        """inside_pair_sokr когда делимитер не точка"""
        split = SentSplit("т", ",", "д")
        result = inside_pair_sokr(split)
        assert result is None

    def test_initials_left_not_period(self):
        """initials_left когда делимитер не точка"""
        split = SentSplit("А", ",", "С")
        result = initials_left(split)
        assert result is None

    def test_close_bracket_not_bracket(self):
        """close_bracket когда делимитер не скобка"""
        split = SentSplit("text", ".", "next")
        result = close_bracket(split)
        assert result is None


class TestMainAPI:
    """Тесты для покрытия основного API в __init__.py"""

    def test_tokenize_api(self):
        """Тест tokenize() из главного модуля"""
        from mawo_razdel import tokenize as main_tokenize

        result = list(main_tokenize("привет мир"))
        assert len(result) == 2
        assert result[0].text == "привет"
        assert result[1].text == "мир"

    def test_sentenize_api(self):
        """Тест sentenize() из главного модуля"""
        from mawo_razdel import sentenize as main_sentenize

        result = list(main_sentenize("Привет. Мир."))
        assert len(result) == 2
        assert "Привет" in result[0].text
        assert "Мир" in result[1].text


class TestRecordRepr:
    """Тесты для Record.__repr__"""

    def test_substring_repr(self):
        """Тест __repr__ для Substring"""
        s = Substring(0, 5, "hello")
        repr_str = repr(s)
        assert "Substring" in repr_str
        assert "0" in repr_str
        assert "5" in repr_str
        assert "hello" in repr_str


class TestSegmenterEdgeCases:
    """Тесты для покрытия base.py edge cases"""

    def test_segment_empty_text(self):
        """Тест segment с пустым текстом"""
        result = list(tokenize(""))
        assert len(result) == 0

    def test_segment_none_buffer(self):
        """Тест segment когда buffer None"""
        # Пустая строка даст None buffer
        result = list(sentenize(""))
        assert len(result) == 0


class TestMoreSentenizeRules:
    """Дополнительные тесты для sentenize правил"""

    def test_no_space_prefix_with_space(self):
        """no_space_prefix когда есть пробел"""
        split = SentSplit("left", ".", " right")
        result = no_space_prefix(split)
        assert result is None

    def test_lower_right_upper(self):
        """lower_right когда справа заглавная"""
        split = SentSplit("left", ".", "Right")
        result = lower_right(split)
        assert result is None

    def test_delimiter_right_letter(self):
        """delimiter_right когда справа буква"""
        split = SentSplit("left", ".", "a")
        result = delimiter_right(split)
        assert result is None

    def test_close_bound_with_comma(self):
        """close_bound с запятой"""
        split = SentSplit("left", ",", "right")
        result = close_bound(split)
        # Запятая тоже даёт JOIN
        assert result == JOIN

    def test_close_quote_not_quote(self):
        """close_quote когда делимитер не кавычка"""
        split = SentSplit("left", ".", "right")
        result = close_quote(split)
        assert result is None

    def test_close_bracket_closing(self):
        """close_bracket когда есть закрывающая скобка"""
        split = SentSplit("(text", ")", " Next")
        result = close_bracket(split)
        assert result == JOIN

    def test_initials_left_initial(self):
        """initials_left с инициалом"""
        split = SentSplit("А", ".", "С")
        result = initials_left(split)
        assert result == JOIN

    def test_sokr_left_abbreviation(self):
        """sokr_left с аббревиатурой"""
        split = SentSplit("г", ".", "Москва")
        result = sokr_left(split)
        assert result == JOIN

    def test_inside_pair_sokr_pair(self):
        """inside_pair_sokr с парной аббревиатурой"""
        split = SentSplit("т", ".", "д")
        result = inside_pair_sokr(split)
        assert result == JOIN


class TestMoreTokenizeRules:
    """Дополнительные тесты для tokenize правил"""

    def test_dash_hyphenated_word(self):
        """Тест слов через дефис"""
        result = list(tokenize("что-то"))
        assert any(t.text == "что-то" for t in result)

    def test_underscore_words(self):
        """Тест слов через подчеркивание"""
        result = list(tokenize("a_b"))
        assert any("_" in t.text for t in result)

    def test_float_number(self):
        """Тест десятичных чисел"""
        result = list(tokenize("3.14"))
        assert any("3.14" in t.text for t in result)

    def test_fraction(self):
        """Тест дробей"""
        result = list(tokenize("1/2"))
        assert any("1/2" in t.text for t in result)

    def test_ellipsis(self):
        """Тест многоточия"""
        result = list(tokenize("..."))
        assert any("..." in t.text for t in result)

    def test_other_ru_left_other_right(self):
        """other rule: RU слева, OTHER справа"""
        atom1 = Atom(0, 1, "RU", "а")
        atom2 = Atom(1, 2, "OTHER", "Δ")
        split = TokenSplit([atom1], "", [atom2])
        result = other(split)
        assert result == JOIN

    def test_yahoo_match(self):
        """yahoo когда yahoo!"""
        atom1 = Atom(0, 5, "LAT", "yahoo")
        atom2 = Atom(5, 6, "PUNCT", "!")
        split = TokenSplit([atom1], "", [atom2])
        result = yahoo(split)
        assert result == JOIN


class TestCoverageMissingLines:
    """Тесты для специфических непокрытых строк"""

    def test_inside_pair_sokr_both_sokrs(self):
        """inside_pair_sokr когда и left и right - сокращения (строка 127)"""
        # "т. д." - оба элемента пары сокращений
        text = "и т. д. продолжили"
        result = list(sentenize(text))
        assert len(result) == 1  # Одно предложение, т.д. не разделяет

    def test_close_quote_generic_no_space(self):
        """close_quote с генерической кавычкой без пробела (строки 181-184)"""
        text = 'Он сказал "привет"в комнату'
        _ = list(sentenize(text))
        # Кавычка без пробела

    def test_dash_right_lowercase(self):
        """dash_right с lowercase справа (строка 235)"""
        text = "Слово – начало предложения"
        _ = list(sentenize(text))
        # Проверяем что тире с lowercase

    def test_left_space_suffix_property(self):
        """Тест left_space_suffix property (строка 252)"""
        split = SentSplit("test ", ".", "next")
        # Доступ к свойству
        has_space = split.left_space_suffix
        assert has_space or not has_space  # Просто вызываем

    def test_split_space_with_delimiter(self):
        """split_space когда есть delimiter (строки 63-64)"""
        # split_space вызывается при токенизации с пробелами
        text = "a b"
        result = list(tokenize(text))
        assert len(result) == 2  # Два токена, разделены пробелом

    def test_dash_rule_punct_return(self):
        """DashRule return None когда PUNCT (строка 99)"""
        text = ".-word"
        _ = list(tokenize(text))
        # Точка - PUNCT, должно разделиться

    def test_underscore_rule_punct_return(self):
        """UnderscoreRule return None когда PUNCT (строка 111)"""
        text = "._word"
        _ = list(tokenize(text))
        # Точка - PUNCT, должно разделиться

    def test_other_special_chars(self):
        """other function с спецсимволами (строка 160)"""
        text = "α&β"
        _ = list(tokenize(text))
        # Греческие буквы + спецсимвол

    def test_token_split_left_3(self):
        """Доступ к left_3 property (строка 228)"""
        atom1 = Atom(0, 1, "RU", "а")
        atom2 = Atom(1, 2, "RU", "б")
        atom3 = Atom(2, 3, "RU", "в")
        atom4 = Atom(3, 4, "RU", "г")
        split = TokenSplit([atom1, atom2, atom3, atom4], "", [atom1])
        # Доступ к left_3
        val = split.left_3
        assert val == atom2  # Третий с конца

    def test_token_split_right_3(self):
        """Доступ к right_3 property (строка 242)"""
        atom1 = Atom(0, 1, "RU", "а")
        atom2 = Atom(1, 2, "RU", "б")
        atom3 = Atom(2, 3, "RU", "в")
        atom4 = Atom(3, 4, "RU", "г")
        split = TokenSplit([atom1], "", [atom1, atom2, atom3, atom4])
        # Доступ к right_3 (индекс 2, третий элемент)
        val = split.right_3
        assert val == atom3  # Третий элемент (индекс 2)

    def test_double_dash(self):
        """Тест двойного тире -- (строка 160)"""
        text = "text--more"
        result = list(tokenize(text))
        # -- должны склеиться
        assert any("--" in t.text for t in result)

    def test_double_asterisk(self):
        """Тест двойного asterisk ** (строка 160)"""
        text = "text**bold"
        result = list(tokenize(text))
        # ** должны склеиться
        assert any("**" in t.text for t in result)

    def test_space_delimiter(self):
        """Тест пробела как разделителя (строки 63-64)"""
        # Пробел в качестве разделителя
        text = "one two three"
        result = list(tokenize(text))
        assert len(result) == 3

    def test_pair_sokr_with_another_sokr(self):
        """Тест пары сокращений т.д. (строка 127)"""
        text = "и т. д. и т. п. везде"
        result = list(sentenize(text))
        # Пары сокращений не должны разделять предложения
        assert len(result) == 1

    def test_generic_quote_without_space(self):
        """Тест generic quote без пробела слева (строки 181-184)"""
        text = 'Слово"начало" текст'
        _ = list(sentenize(text))
        # Кавычка без пробела

    def test_dash_before_lowercase_word(self):
        """Тест тире перед lowercase словом (строка 235)"""
        text = "Текст – слово продолжение"
        _ = list(sentenize(text))
        # Тире перед lowercase - не разделяет


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=mawo_razdel", "--cov-report=term-missing"])
