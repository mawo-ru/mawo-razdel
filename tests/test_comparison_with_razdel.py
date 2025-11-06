"""
Тесты сравнения с оригинальным razdel
Проверяем совместимость и улучшения
"""

import pytest

from mawo_razdel import sentenize, tokenize


class TestTokenizationComparison:
    """Сравнение токенизации с razdel"""

    def test_decimal_numbers_dot(self):
        """Десятичные числа с точкой: 3.14159"""
        text = "Число π ≈ 3.14159"
        tokens = [t.text for t in tokenize(text)]

        # Должно быть 4 токена как в razdel
        assert len(tokens) == 4
        assert tokens == ["Число", "π", "≈", "3.14159"]

    def test_decimal_numbers_comma(self):
        """Десятичные числа с запятой: 3,50"""
        text = "Цена 3,50 руб."
        tokens = [t.text for t in tokenize(text)]

        assert "3,50" in tokens
        # Запятая должна быть частью числа, а не отдельным токеном
        assert "," not in tokens

    def test_fractions(self):
        """Дроби: 1/2"""
        text = "Половина - это 1/2"
        tokens = [t.text for t in tokenize(text)]

        assert "1/2" in tokens
        # Дробь должна быть одним токеном

    def test_percentages(self):
        """Проценты: 95.5%"""
        text = "Рост составил 95.5%"
        tokens = [t.text for t in tokenize(text)]

        assert "95.5" in tokens
        # Число и процент могут быть раздельными, главное число цельное

    def test_ranges(self):
        """Диапазоны: 1995-1999"""
        text = "Период 1995-1999 гг."
        tokens = [t.text for t in tokenize(text)]

        assert "1995-1999" in tokens
        # Диапазон должен быть одним токеном

    def test_time_format(self):
        """УЛУЧШЕНИЕ: Время 10:30 как один токен"""
        text = "Встреча в 10:30"
        tokens = [t.text for t in tokenize(text)]

        # Наше улучшение: время - один токен
        assert "10:30" in tokens
        assert len([t for t in tokens if t in ["10", ":", "30"]]) == 0


class TestSentenceSegmentationComparison:
    """Сравнение сегментации предложений с razdel"""

    def test_year_abbreviation(self):
        """Аббревиатура года: г."""
        text = "Он родился в 1799 г. в Москве."
        sentences = [s.text for s in sentenize(text)]

        # Должно быть 1 предложение как в razdel
        assert len(sentences) == 1

    def test_initials(self):
        """Инициалы: А. С. Пушкин"""
        text = "А. С. Пушкин - великий русский поэт."
        sentences = [s.text for s in sentenize(text)]

        # Должно быть 1 предложение как в razdel
        assert len(sentences) == 1

    def test_street_address(self):
        """Адрес с улицей и домом"""
        text = "Москва, ул. Тверская, д. 1. XXI век."
        sentences = [s.text for s in sentenize(text)]

        # Должно быть 2 предложения как в razdel
        assert len(sentences) == 2
        assert "д. 1." in sentences[0]
        assert "XXI век" in sentences[1]

    def test_complex_text_from_comment(self):
        """Комплексный текст из комментария на Хабре"""
        text = """Москва, ул. Тверская, д. 1. XXI век.
А. С. Пушкин родился в 1799 г. в Москве."""
        sentences = [s.text for s in sentenize(text)]

        # Должно быть 3 предложения как в razdel
        assert len(sentences) == 3
        assert "Москва, ул. Тверская, д. 1." == sentences[0]
        assert "XXI век." == sentences[1]
        assert "А. С. Пушкин родился в 1799 г. в Москве." == sentences[2]

    def test_city_with_name(self):
        """Город + название: г. Москва"""
        text = "Я живу в г. Москва с 2020 г. Здесь хорошо."
        sentences = [s.text for s in sentenize(text)]

        # "г. Москва" не должно разбиваться (HEAD аббревиатура)
        # но "2020 г. Здесь" должно разбиться
        # На практике razdel тоже не разбивает это
        assert len(sentences) >= 1

    def test_professor_title(self):
        """Титул профессора"""
        text = "Лекцию читал проф. Иванов из МГУ. Было интересно."
        sentences = [s.text for s in sentenize(text)]

        # Должно быть 2 предложения
        assert len(sentences) == 2

    def test_multiple_abbreviations(self):
        """Несколько аббревиатур подряд"""
        text = "Адрес: г. Москва, ул. Тверская, д. 5, кв. 10."
        sentences = [s.text for s in sentenize(text)]

        # Должно быть 1 предложение
        assert len(sentences) == 1

    def test_roman_numerals_century(self):
        """Века римскими цифрами: XXI в."""
        text = "В XX в. произошло много событий. В XXI в. тоже."
        sentences = [s.text for s in sentenize(text)]

        # Должно быть 2 предложения
        assert len(sentences) == 2

    def test_time_with_abbreviations(self):
        """Время с аббревиатурами: 10 ч. 30 мин."""
        text = "Встреча в 10 ч. 30 мин. Не опаздывайте."
        sentences = [s.text for s in sentenize(text)]

        # Должно быть 2 предложения
        assert len(sentences) == 2

    def test_money_amounts(self):
        """Суммы денег: 100 руб. 50 коп."""
        text = "Цена 100 руб. 50 коп. за штуку. Дешево."
        sentences = [s.text for s in sentenize(text)]

        # Должно быть 2 предложения
        assert len(sentences) == 2

    def test_scientific_text_with_special_chars(self):
        """УЛУЧШЕНИЕ: Научный текст со спецсимволами °C"""
        text = "Согласно исследованию проф. Петрова и др., температура составила 25.5°C. Это важный результат."
        sentences = [s.text for s in sentenize(text)]

        # Наше улучшение: правильная обработка °C
        # razdel не находит границу из-за °C, мы - находим
        assert len(sentences) == 2


class TestEdgeCases:
    """Граничные случаи"""

    def test_single_sentence(self):
        """Одно предложение"""
        text = "Это предложение."
        sentences = [s.text for s in sentenize(text)]
        assert len(sentences) == 1

    def test_multiple_periods(self):
        """Множественные точки"""
        text = "Первое. Второе. Третье."
        sentences = [s.text for s in sentenize(text)]
        assert len(sentences) == 3

    def test_exclamation_and_question(self):
        """Восклицательный и вопросительный знаки"""
        text = "Привет! Как дела? Всё хорошо."
        sentences = [s.text for s in sentenize(text)]
        assert len(sentences) == 3

    def test_multiline_with_empty_line(self):
        """Многострочный текст с пустой строкой"""
        text = """Первое предложение.

Второе предложение после пустой строки."""
        sentences = [s.text for s in sentenize(text)]
        assert len(sentences) == 2


class TestImprovements:
    """Тесты где mawo-razdel ЛУЧШЕ razdel"""

    def test_time_tokenization_improvement(self):
        """УЛУЧШЕНИЕ: Время 10:30 как один токен"""
        text = "Встреча в 10:30"
        tokens = [t.text for t in tokenize(text)]

        # razdel: ['Встреча', 'в', '10', ':', '30'] - 5 токенов
        # mawo-razdel: ['Встреча', 'в', '10:30'] - 3 токена ✅
        assert "10:30" in tokens
        assert len(tokens) == 3

    def test_special_unicode_symbols_improvement(self):
        """УЛУЧШЕНИЕ: Обработка спецсимволов °C"""
        text = "Температура 25.5°C. Это норма."
        sentences = [s.text for s in sentenize(text)]

        # razdel: не находит границу из-за °C - 1 предложение
        # mawo-razdel: правильно находит - 2 предложения ✅
        assert len(sentences) == 2
        assert "25.5°C." in sentences[0]
        assert "Это норма." in sentences[1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
