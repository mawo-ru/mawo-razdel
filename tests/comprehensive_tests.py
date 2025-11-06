"""
Расширенные строгие тесты для mawo-razdel
Проверяем все edge cases и ищем где мы лучше razdel

Этот скрипт можно запускать напрямую для быстрой проверки всех случаев.
Для pytest-тестов используйте test_comparison_with_razdel.py
"""

import sys
from pathlib import Path

# Добавляем путь к библиотеке если запускаем как standalone скрипт
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

from razdel import sentenize as rsentenize, tokenize as rtokenize

from mawo_razdel import sentenize, tokenize


def test_case(name, text, func_razdel, func_mawo, expected=None, verbose=False):
    """Тестовый случай"""
    razdel_res = list(func_razdel(text))
    mawo_res = list(func_mawo(text))

    razdel_texts = [v.text for v in razdel_res]
    mawo_texts = [v.text for v in mawo_res]

    match = razdel_texts == mawo_texts
    better = False

    if expected:
        better = mawo_texts == expected and razdel_texts != expected

    status = "✅" if match else ("🏆" if better else "❌")

    print(f"\n{status} {name}")
    print(f"   Razdel: {len(razdel_res)} | Mawo: {len(mawo_res)}")

    if verbose or not match:
        print(f"   Razdel: {razdel_texts}")
        print(f"   Mawo:   {mawo_texts}")
        if expected:
            print(f"   Ожидается: {expected}")

    return match or better


print("=" * 80)
print("ТЕСТЫ ТОКЕНИЗАЦИИ")
print("=" * 80)

results = []

# Десятичные числа
results.append(test_case(
    "Десятичное число (точка)",
    "Число π ≈ 3.14159",
    rtokenize, tokenize,
    verbose=True
))

results.append(test_case(
    "Десятичное число (запятая)",
    "Цена 3,50 руб.",
    rtokenize, tokenize,
    verbose=True
))

# Дроби
results.append(test_case(
    "Дробь",
    "Половина - это 1/2",
    rtokenize, tokenize,
    verbose=True
))

# Процент
results.append(test_case(
    "Процент",
    "Рост составил 95.5%",
    rtokenize, tokenize,
    verbose=True
))

# Диапазоны
results.append(test_case(
    "Диапазон годов",
    "Период 1995-1999 гг.",
    rtokenize, tokenize,
    verbose=True
))

# Время
results.append(test_case(
    "Время",
    "Встреча в 10:30",
    rtokenize, tokenize,
    verbose=True
))

print("\n" + "=" * 80)
print("ТЕСТЫ СЕГМЕНТАЦИИ")
print("=" * 80)

# Аббревиатуры
results.append(test_case(
    "Год (г.)",
    "Он родился в 1799 г. в Москве.",
    rsentenize, sentenize
))

results.append(test_case(
    "Инициалы",
    "А. С. Пушкин - великий русский поэт.",
    rsentenize, sentenize
))

results.append(test_case(
    "Адрес",
    "Москва, ул. Тверская, д. 1. XXI век.",
    rsentenize, sentenize,
    verbose=True
))

results.append(test_case(
    "Комплексный текст",
    """Москва, ул. Тверская, д. 1. XXI век.
А. С. Пушкин родился в 1799 г. в Москве.""",
    rsentenize, sentenize,
    verbose=True
))

# Сложные случаи
results.append(test_case(
    "Город + название",
    "Я живу в г. Москва с 2020 г. Здесь хорошо.",
    rsentenize, sentenize,
    verbose=True
))

results.append(test_case(
    "Профессор",
    "Лекцию читал проф. Иванов из МГУ. Было интересно.",
    rsentenize, sentenize,
    verbose=True
))

results.append(test_case(
    "Несколько аббревиатур",
    "Адрес: г. Москва, ул. Тверская, д. 5, кв. 10.",
    rsentenize, sentenize,
    verbose=True
))

results.append(test_case(
    "Век римскими цифрами",
    "В XX в. произошло много событий. В XXI в. тоже.",
    rsentenize, sentenize,
    verbose=True
))

results.append(test_case(
    "Время с аббревиатурой",
    "Встреча в 10 ч. 30 мин. Не опаздывайте.",
    rsentenize, sentenize,
    verbose=True
))

results.append(test_case(
    "Деньги",
    "Цена 100 руб. 50 коп. за штуку. Дешево.",
    rsentenize, sentenize,
    verbose=True
))

# Edge cases
results.append(test_case(
    "Точка в конце строки",
    "Это предложение.",
    rsentenize, sentenize
))

results.append(test_case(
    "Множественные точки",
    "Первое. Второе. Третье.",
    rsentenize, sentenize
))

results.append(test_case(
    "Восклицательный знак",
    "Привет! Как дела? Всё хорошо.",
    rsentenize, sentenize
))

results.append(test_case(
    "Многострочный текст",
    """Первое предложение.

Второе предложение после пустой строки.""",
    rsentenize, sentenize,
    verbose=True
))

# Научный текст
results.append(test_case(
    "Научный текст",
    "Согласно исследованию проф. Петрова и др., температура составила 25.5°C. Это важный результат.",
    rsentenize, sentenize,
    verbose=True
))

print("\n" + "=" * 80)
print("ИТОГОВАЯ СТАТИСТИКА")
print("=" * 80)

total = len(results)
passed = sum(results)
failed = total - passed

print(f"Всего тестов: {total}")
print(f"Пройдено: {passed} ({100*passed//total}%)")
print(f"Не пройдено: {failed}")

if failed == 0:
    print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Библиотека работает корректно!")
else:
    print(f"\n⚠️  Нужно исправить {failed} тест(ов)")
