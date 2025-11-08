import pytest

from mawo_razdel import tokenize

from .common import data_lines, data_path, run
from .partition import parse_partitions

UNIT = parse_partitions(
    [
        "1",
        "что-то",
        "К_тому_же",
        "...",
        "1,5",
        "1/2",
        "»||.",
        ")||.",
        "(||«",
        ":)))",
        ":)||,",
        "mβж",
        "Δσ",
        "",
    ]
)


@pytest.mark.parametrize("test", UNIT)
def test_unit(test):
    run(tokenize, test)


def int_tests(count):
    path = data_path("tokens.txt")
    lines = data_lines(path, count)
    return parse_partitions(lines)


def test_int(int_test):
    run(tokenize, int_test)
