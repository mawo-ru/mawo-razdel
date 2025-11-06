"""
Тесты из комментария на Хабре
https://habr.com/ru/articles/963748/

Это точные тесты, которые предложил комментатор для проверки библиотеки.
Все эти тесты должны проходить и показывать идентичные результаты с razdel.
"""

import pytest

from mawo_razdel import sentenize, tokenize

# Импортируем razdel для сравнения (опционально)
try:
    from razdel import sentenize as rsentenize
    from razdel import tokenize as rtokenize

    RAZDEL_AVAILABLE = True
except ImportError:
    RAZDEL_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="razdel not installed")


class TestHabrCommentCases:
    """Точные тесты из комментария на Хабре"""

    def test_year_abbreviation_case(self):
        """Тест 1 из комментария: Он родился в 1799 г. в Москве."""
        text = "Он родился в 1799 г. в Москве."

        mawo_res = list(sentenize(text))
        razdel_res = list(rsentenize(text))

        # Должно быть 1 предложение как в razdel
        assert len(mawo_res) == len(razdel_res) == 1
        assert mawo_res[0].text == razdel_res[0].text

    def test_initials_case(self):
        """Тест 2 из комментария: А. С. Пушкин - великий русский поэт."""
        text = "А. С. Пушкин - великий русский поэт."

        mawo_res = list(sentenize(text))
        razdel_res = list(rsentenize(text))

        # Должно быть 1 предложение как в razdel
        assert len(mawo_res) == len(razdel_res) == 1
        assert mawo_res[0].text == razdel_res[0].text

    def test_pi_number_tokenization(self):
        """Тест 3 из комментария: Число π ≈ 3.14159"""
        text = "Число π ≈ 3.14159"

        mawo_tokens = [t.text for t in tokenize(text)]
        razdel_tokens = [t.text for t in rtokenize(text)]

        # razdel: ['Число', 'π', '≈', '3.14159'] - 4 токена
        # mawo-razdel должен давать такой же результат
        assert len(mawo_tokens) == len(razdel_tokens) == 4
        assert mawo_tokens == razdel_tokens
        assert mawo_tokens == ["Число", "π", "≈", "3.14159"]

    def test_complex_text_case(self):
        """Тест 4 из комментария: Комплексный текст с адресом"""
        text = """Москва, ул. Тверская, д. 1. XXI век.
А. С. Пушкин родился в 1799 г. в Москве."""

        mawo_res = [s.text for s in sentenize(text)]
        razdel_res = [s.text for s in rsentenize(text)]

        # razdel: 3 предложения
        # mawo-razdel должен давать такой же результат
        assert len(mawo_res) == len(razdel_res) == 3

        # Проверяем каждое предложение
        assert mawo_res[0] == razdel_res[0]
        assert "Москва, ул. Тверская, д. 1." == mawo_res[0]

        assert mawo_res[1] == razdel_res[1]
        assert "XXI век." == mawo_res[1]

        assert mawo_res[2] == razdel_res[2]
        assert "А. С. Пушкин родился в 1799 г. в Москве." == mawo_res[2]


class TestHabrCommentSummary:
    """Итоговая проверка всех случаев из комментария"""

    def test_all_four_cases_match_razdel(self):
        """Проверка что все 4 теста из комментария дают результаты как в razdel"""

        # Тест 1: Год
        text1 = "Он родился в 1799 г. в Москве."
        assert len(list(sentenize(text1))) == len(list(rsentenize(text1)))

        # Тест 2: Инициалы
        text2 = "А. С. Пушкин - великий русский поэт."
        assert len(list(sentenize(text2))) == len(list(rsentenize(text2)))

        # Тест 3: Число π
        text3 = "Число π ≈ 3.14159"
        mawo_tokens = [t.text for t in tokenize(text3)]
        razdel_tokens = [t.text for t in rtokenize(text3)]
        assert mawo_tokens == razdel_tokens

        # Тест 4: Комплексный
        text4 = """Москва, ул. Тверская, д. 1. XXI век.
А. С. Пушкин родился в 1799 г. в Москве."""
        mawo_sents = [s.text for s in sentenize(text4)]
        razdel_sents = [s.text for s in rsentenize(text4)]
        assert len(mawo_sents) == len(razdel_sents) == 3
        assert mawo_sents == razdel_sents


class TestHabrCommentStandalone:
    """Тесты без зависимости от razdel - работают всегда"""

    def test_year_abbreviation_standalone(self):
        """Он родился в 1799 г. в Москве."""
        text = "Он родился в 1799 г. в Москве."
        sentences = list(sentenize(text))

        assert len(sentences) == 1
        assert sentences[0].text == text

    def test_initials_standalone(self):
        """А. С. Пушкин - великий русский поэт."""
        text = "А. С. Пушкин - великий русский поэт."
        sentences = list(sentenize(text))

        assert len(sentences) == 1
        assert sentences[0].text == text

    def test_pi_number_standalone(self):
        """Число π ≈ 3.14159"""
        text = "Число π ≈ 3.14159"
        tokens = [t.text for t in tokenize(text)]

        assert len(tokens) == 4
        assert tokens == ["Число", "π", "≈", "3.14159"]

    def test_complex_text_standalone(self):
        """Комплексный текст с адресом"""
        text = """Москва, ул. Тверская, д. 1. XXI век.
А. С. Пушкин родился в 1799 г. в Москве."""

        sentences = [s.text for s in sentenize(text)]

        assert len(sentences) == 3
        assert sentences[0] == "Москва, ул. Тверская, д. 1."
        assert sentences[1] == "XXI век."
        assert sentences[2] == "А. С. Пушкин родился в 1799 г. в Москве."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
