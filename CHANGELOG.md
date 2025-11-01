# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-11-01

### Fixed
- Полная совместимость с Python 3.9+ (убраны variable-width look-behind regex)
- Обратная совместимость API: sentenize и tokenize возвращают Substring объекты
- Исправлены позиции start/stop в токенах и предложениях
- Переписана логика поиска границ предложений без использования сложных regex
- Все 29 тестов успешно проходят на Python 3.9-3.13

### Changed
- Улучшена логика блокировки границ предложений
- Оптимизирована обработка аббревиатур, инициалов и десятичных чисел

## [1.0.0] - 2025-11-01

### Added
- Initial release of mawo-razdel
- Advanced Russian tokenization with SynTagRus patterns
- 80+ abbreviations support (г., ул., т.д., и т.п., и др.)
- Initials handling (А. С. Пушкин)
- Direct speech pattern support
- Decimal numbers recognition (3.14 as single token)
- Quality assessment function `get_segmentation_quality()`
- Comprehensive test suite with 29+ test cases
- Full type hints support with `py.typed`

### Features
- **Tokenization**: Fast word and punctuation tokenization (~5000 tokens/sec)
- **Sentence segmentation**: Enhanced segmentation with +25% accuracy on news texts
- **SynTagRus patterns**: Based on Russian dependency treebank
- **Corpus data**: Pre-compressed LZMA corpora (OpenCorpora, GICRYA, RNC, SynTagRus)
- **Zero dependencies**: No external runtime dependencies
- **Python 3.10+**: Modern Python support

### Technical
- MIT License
- Based on original Razdel by Alexander Kukushkin
- Enhanced by MAWO Team with improved patterns and quality metrics

[1.0.0]: https://github.com/mawo-ru/mawo-razdel/releases/tag/v1.0.0
