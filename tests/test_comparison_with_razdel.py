"""Тесты на совместимость с оригинальным razdel"""

import pytest

from mawo_razdel import sentenize, tokenize


class TestTokenizationComparison:
    """Сравнение токенизации с razdel"""

    def test_decimal_numbers_dot(self):
        """Десятичные числа с точкой"""
        text = "Число π примерно равно 3.14159"
        tokens = [t.text for t in tokenize(text)]

        # razdel склеивает десятичные числа
        assert "3.14159" in tokens

    def test_decimal_numbers_comma(self):
        """Десятичные числа с запятой"""
        text = "Температура 36,6 градусов"
        tokens = [t.text for t in tokenize(text)]

        # razdel склеивает десятичные числа с запятой
        assert "36,6" in tokens

    def test_fractions(self):
        """Дроби"""
        text = "Это примерно 1/2 от целого"
        tokens = [t.text for t in tokenize(text)]

        # razdel склеивает дроби
        assert "1/2" in tokens

    def test_percentages(self):
        """Проценты"""
        text = "Рост составил 15.5%"
        tokens = [t.text for t in tokenize(text)]

        # razdel: процент отдельно, число с точкой вместе
        assert "15.5" in tokens
        assert "%" in tokens

    def test_ranges(self):
        """Диапазоны"""
        text = "В период 1995-1999 годов"
        tokens = [t.text for t in tokenize(text)]

        assert "1995-1999" in tokens
        # Диапазон должен быть одним токеном

    def test_time_format(self):
        """Время 10:30 токенизируется как оригинальный razdel"""
        text = "Встреча в 10:30"
        tokens = [t.text for t in tokenize(text)]

        # Совместимость с razdel: время разбивается на части
        assert "10" in tokens
        assert ":" in tokens
        assert "30" in tokens


class TestSentenceSegmentationComparison:
    """Сравнение сегментации предложений с razdel"""

    def test_year_abbreviation(self):
        """Аббревиатура года"""
        text = "Он родился в 1799 г. в Москве"
        sentences = [s.text for s in sentenize(text)]

        # Должно быть одно предложение - "г." это аббревиатура
        assert len(sentences) == 1

    def test_initials(self):
        """Инициалы"""
        text = "А. С. Пушкин был великим поэтом"
        sentences = [s.text for s in sentenize(text)]

        # Должно быть одно предложение - инициалы не разделяют
        assert len(sentences) == 1

    def test_street_address(self):
        """Адрес с сокращениями"""
        text = "Москва, ул. Тверская, д. 1. Здесь жил поэт."
        sentences = [s.text for s in sentenize(text)]

        # Должно быть 2 предложения
        assert len(sentences) == 2

    def test_complex_text_from_comment(self):
        """Сложный текст из комментария"""
        text = """Москва, ул. Тверская, д. 1. XXI век.
А. С. Пушкин родился в 1799 г. в Москве."""
        sentences = [s.text for s in sentenize(text)]

        # Должно быть 3 предложения
        assert len(sentences) == 3

    def test_city_with_name(self):
        """Город с сокращением"""
        text = "Родился в г. Москве"
        sentences = [s.text for s in sentenize(text)]

        # Одно предложение
        assert len(sentences) == 1

    def test_professor_title(self):
        """Звание профессора"""
        text = "Работа проф. Иванова была важна"
        sentences = [s.text for s in sentenize(text)]

        # Одно предложение
        assert len(sentences) == 1

    def test_multiple_abbreviations(self):
        """Несколько аббревиатур подряд"""
        text = "И т. д. и т. п. В общем, вся газета"
        sentences = [s.text for s in sentenize(text)]

        # Должно быть 2 предложения
        assert len(sentences) == 2

    def test_roman_numerals_century(self):
        """Римские цифры для веков"""
        text = "Это было в XIX в. в России"
        sentences = [s.text for s in sentenize(text)]

        # Одно предложение
        assert len(sentences) == 1

    def test_time_with_abbreviations(self):
        """Время с сокращениями"""
        text = "Встреча в 15 час. 30 мин. началась"
        sentences = [s.text for s in sentenize(text)]

        # Одно предложение
        assert len(sentences) == 1

    def test_money_amounts(self):
        """Денежные суммы"""
        text = "Цена 100 руб. за штуку"
        sentences = [s.text for s in sentenize(text)]

        # Одно предложение
        assert len(sentences) == 1

    def test_scientific_text_with_special_chars(self):
        """Научный текст со спецсимволами °C как в оригинальном razdel"""
        text = "Согласно исследованию проф. Петрова и др., температура составила 25.5°C. Это важный результат."
        sentences = [s.text for s in sentenize(text)]

        # Совместимость с razdel: °C не даёт разделить предложение
        assert len(sentences) == 1


class TestEdgeCases:
    """Граничные случаи"""

    def test_single_sentence(self):
        """Один простой текст"""
        text = "Это простое предложение"
        sentences = [s.text for s in sentenize(text)]

        assert len(sentences) == 1

    def test_multiple_periods(self):
        """Многоточие"""
        text = "Подожди... Что это?"
        sentences = [s.text for s in sentenize(text)]

        # Должно быть 2 предложения
        assert len(sentences) == 2

    def test_exclamation_and_question(self):
        """Восклицание и вопрос"""
        text = "Привет! Как дела?"
        sentences = [s.text for s in sentenize(text)]

        # 2 предложения
        assert len(sentences) == 2

    def test_multiline_with_empty_line(self):
        """Многострочный текст с пустой строкой"""
        text = """Первое предложение.

Второе предложение."""
        sentences = [s.text for s in sentenize(text)]

        # Должно быть 2 предложения
        assert len(sentences) == 2


class TestCompatibility:
    """Тесты на 100% совместимость с оригинальным razdel"""

    def test_time_tokenization_compatibility(self):
        """Время 10:30 токенизируется как в razdel (части)"""
        text = "Встреча в 10:30"
        tokens = [t.text for t in tokenize(text)]

        # 100% совместимость с razdel: время разбивается
        assert "10" in tokens
        assert ":" in tokens
        assert "30" in tokens
        assert len(tokens) == 5

    def test_special_unicode_symbols_compatibility(self):
        """Обработка спецсимволов °C как в razdel"""
        text = "Температура 25.5°C. Это норма."
        sentences = [s.text for s in sentenize(text)]

        # 100% совместимость с razdel: °C не разделяет
        assert len(sentences) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
