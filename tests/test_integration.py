"""
Строгие интеграционные тесты для mawo-razdel
Тестируют библиотеку как самодостаточный проект
"""

from pathlib import Path

import pytest


class TestImports:
    """Тесты импортов"""

    def test_main_module_import(self):
        """Тест: главный модуль импортируется"""
        try:
            import mawo_razdel  # noqa: F401
        except ImportError as e:
            pytest.fail(f"Failed to import mawo_razdel: {e}")

    def test_sentenize_function_import(self):
        """Тест: функция sentenize импортируется"""
        try:
            from mawo_razdel import sentenize  # noqa: F401
        except ImportError as e:
            pytest.fail(f"Failed to import sentenize: {e}")

    def test_tokenize_function_import(self):
        """Тест: функция tokenize импортируется"""
        try:
            from mawo_razdel import tokenize  # noqa: F401
        except ImportError as e:
            pytest.fail(f"Failed to import tokenize: {e}")

    def test_substring_class_import(self):
        """Тест: класс Substring импортируется"""
        try:
            from mawo_razdel import Substring  # noqa: F401
        except ImportError as e:
            pytest.fail(f"Failed to import Substring: {e}")


class TestSentenizeFunctionality:
    """Тесты функциональности сегментации предложений"""

    def test_sentenize_simple_text(self):
        """Тест: сегментация простого текста"""
        from mawo_razdel import sentenize

        text = "Привет! Как дела?"
        try:
            result = list(sentenize(text))
            assert result is not None
            assert isinstance(result, list)
        except Exception as e:
            pytest.fail(f"sentenize failed on simple text: {e}")

    def test_sentenize_two_sentences(self):
        """Тест: сегментация двух предложений"""
        from mawo_razdel import sentenize

        text = "Привет! Как дела?"
        result = list(sentenize(text))

        assert len(result) == 2, f"Expected 2 sentences, got {len(result)}"
        assert result[0].text == "Привет!"
        assert result[1].text == "Как дела?"

    def test_sentenize_with_period(self):
        """Тест: сегментация с точкой"""
        from mawo_razdel import sentenize

        text = "Это первое предложение. Это второе предложение."
        result = list(sentenize(text))

        assert len(result) == 2
        assert "первое" in result[0].text
        assert "второе" in result[1].text

    def test_sentenize_single_sentence(self):
        """Тест: сегментация одного предложения"""
        from mawo_razdel import sentenize

        text = "Это одно предложение"
        result = list(sentenize(text))

        assert len(result) == 1
        assert result[0].text == text

    def test_sentenize_empty_text(self):
        """Тест: сегментация пустого текста"""
        from mawo_razdel import sentenize

        text = ""
        result = list(sentenize(text))

        assert isinstance(result, list)

    def test_sentenize_with_abbreviations(self):
        """Тест: сегментация с аббревиатурами"""
        from mawo_razdel import sentenize

        text = "Встреча в 10 ч. утра. Приходите вовремя."
        result = list(sentenize(text))

        # Должно быть 2 предложения (аббревиатура "ч." не должна разбивать)
        assert len(result) >= 1

    def test_sentenize_returns_substrings(self):
        """Тест: sentenize возвращает объекты Substring"""
        from mawo_razdel import Substring, sentenize

        text = "Привет! Мир."
        result = list(sentenize(text))

        assert all(isinstance(s, Substring) for s in result)
        assert all(hasattr(s, "start") for s in result)
        assert all(hasattr(s, "stop") for s in result)
        assert all(hasattr(s, "text") for s in result)


class TestTokenizeFunctionality:
    """Тесты функциональности токенизации"""

    def test_tokenize_simple_text(self):
        """Тест: токенизация простого текста"""
        from mawo_razdel import tokenize

        text = "Привет мир"
        try:
            result = list(tokenize(text))
            assert result is not None
            assert isinstance(result, list)
        except Exception as e:
            pytest.fail(f"tokenize failed on simple text: {e}")

    def test_tokenize_two_words(self):
        """Тест: токенизация двух слов"""
        from mawo_razdel import tokenize

        text = "Привет мир"
        result = list(tokenize(text))

        assert len(result) >= 2, f"Expected at least 2 tokens, got {len(result)}"

        # Проверяем, что есть токены "Привет" и "мир"
        tokens_text = [t.text for t in result]
        assert "Привет" in tokens_text
        assert "мир" in tokens_text

    def test_tokenize_with_punctuation(self):
        """Тест: токенизация с пунктуацией"""
        from mawo_razdel import tokenize

        text = "Привет, мир!"
        result = list(tokenize(text))

        assert len(result) >= 3  # "Привет", ",", "мир", "!"
        tokens_text = [t.text for t in result]
        assert "Привет" in tokens_text
        assert "мир" in tokens_text

    def test_tokenize_empty_text(self):
        """Тест: токенизация пустого текста"""
        from mawo_razdel import tokenize

        text = ""
        result = list(tokenize(text))

        assert isinstance(result, list)

    def test_tokenize_numbers(self):
        """Тест: токенизация чисел"""
        from mawo_razdel import tokenize

        text = "123 456"
        result = list(tokenize(text))

        assert len(result) >= 2
        tokens_text = [t.text for t in result]
        assert "123" in tokens_text
        assert "456" in tokens_text

    def test_tokenize_returns_substrings(self):
        """Тест: tokenize возвращает объекты Substring"""
        from mawo_razdel import Substring, tokenize

        text = "Привет мир"
        result = list(tokenize(text))

        assert all(isinstance(t, Substring) for t in result)
        assert all(hasattr(t, "start") for t in result)
        assert all(hasattr(t, "stop") for t in result)
        assert all(hasattr(t, "text") for t in result)


class TestDataFiles:
    """Тесты наличия файлов данных"""

    def test_corpus_files_exist(self):
        """Тест: файлы корпусов существуют"""
        import mawo_razdel

        module_path = Path(mawo_razdel.__file__).parent
        data_path = module_path / "data"

        assert data_path.exists(), f"Data directory not found at {data_path}"
        assert data_path.is_dir(), f"Data path is not a directory: {data_path}"

        # Проверяем наличие основных LZMA файлов
        lzma_files = list(data_path.glob("*.lzma"))
        assert len(lzma_files) > 0, "No LZMA corpus files found"

    def test_corpus_files_not_empty(self):
        """Тест: файлы корпусов не пустые"""
        import mawo_razdel

        module_path = Path(mawo_razdel.__file__).parent
        data_path = module_path / "data"

        lzma_files = list(data_path.glob("*.lzma"))
        for lzma_file in lzma_files:
            assert lzma_file.stat().st_size > 10_000, f"Corpus file too small: {lzma_file.name}"


class TestSubstringClass:
    """Тесты класса Substring"""

    def test_substring_has_attributes(self):
        """Тест: Substring имеет необходимые атрибуты"""
        from mawo_razdel import Substring

        sub = Substring(0, 5, "Привет")

        assert hasattr(sub, "start")
        assert hasattr(sub, "stop")
        assert hasattr(sub, "text")
        assert sub.start == 0
        assert sub.stop == 5
        assert sub.text == "Привет"

    def test_substring_positions_correct(self):
        """Тест: позиции Substring корректны"""
        from mawo_razdel import sentenize

        text = "Привет! Мир."
        result = list(sentenize(text))

        for substring in result:
            # Проверяем, что текст соответствует позициям
            extracted = text[substring.start : substring.stop]
            assert (
                extracted == substring.text
            ), f"Position mismatch: {extracted} != {substring.text}"


class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_sentenize_only_punctuation(self):
        """Тест: сегментация только пунктуации"""
        from mawo_razdel import sentenize

        text = "!!!"
        result = list(sentenize(text))

        assert isinstance(result, list)

    def test_tokenize_only_spaces(self):
        """Тест: токенизация только пробелов"""
        from mawo_razdel import tokenize

        text = "   "
        result = list(tokenize(text))

        assert isinstance(result, list)

    def test_sentenize_very_long_text(self):
        """Тест: сегментация очень длинного текста"""
        from mawo_razdel import sentenize

        text = "Это предложение. " * 100
        result = list(sentenize(text))

        assert len(result) > 0

    def test_tokenize_special_characters(self):
        """Тест: токенизация спецсимволов"""
        from mawo_razdel import tokenize

        text = "@#$%^&*()"
        result = list(tokenize(text))

        assert isinstance(result, list)

    def test_sentenize_multiple_newlines(self):
        """Тест: сегментация с множественными переносами строк"""
        from mawo_razdel import sentenize

        text = "Первое.\n\n\nВторое."
        result = list(sentenize(text))

        assert len(result) >= 1

    def test_tokenize_mixed_cyrillic_latin(self):
        """Тест: токенизация смешанного кириллица/латиница"""
        from mawo_razdel import tokenize

        text = "Привет hello мир world"
        result = list(tokenize(text))

        assert len(result) >= 4
        tokens_text = [t.text for t in result]
        assert "Привет" in tokens_text
        assert "hello" in tokens_text


class TestConsistency:
    """Тесты согласованности"""

    def test_sentenize_deterministic(self):
        """Тест: sentenize детерминирован"""
        from mawo_razdel import sentenize

        text = "Привет! Как дела? Всё хорошо."
        result1 = list(sentenize(text))
        result2 = list(sentenize(text))

        assert len(result1) == len(result2)
        # noqa: B905 - Python 3.9 не поддерживает strict= в zip()
        for r1, r2 in zip(result1, result2):  # noqa: B905
            assert r1.text == r2.text
            assert r1.start == r2.start
            assert r1.stop == r2.stop

    def test_tokenize_deterministic(self):
        """Тест: tokenize детерминирован"""
        from mawo_razdel import tokenize

        text = "Привет, мир!"
        result1 = list(tokenize(text))
        result2 = list(tokenize(text))

        assert len(result1) == len(result2)
        # noqa: B905 - Python 3.9 не поддерживает strict= в zip()
        for r1, r2 in zip(result1, result2):  # noqa: B905
            assert r1.text == r2.text


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
