
import re

from mawo_razdel import Substring


FILL = ' '
FILL_PATTERN = re.compile(r'^\s*$')


class Record:
    """Simple base class for records."""
    __attributes__ = []

    def __repr__(self):
        name = self.__class__.__name__
        args = ', '.join(
            '{0}={1!r}'.format(name, getattr(self, name))
            for name in self.__attributes__
        )
        return '{0}({1})'.format(name, args)

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and all(
                getattr(self, name) == getattr(other, name)
                for name in self.__attributes__
            )
        )

    def __ne__(self, other):
        return not self == other


class Partition(Record):
    __attributes__ = ['chunks']

    is_fill = FILL_PATTERN.match

    def __init__(self, chunks):
        self.chunks = chunks

    @property
    def text(self):
        return ''.join(self.chunks)

    @property
    def substrings(self):
        start = 0
        for chunk in self.chunks:
            stop = start + len(chunk)
            if not self.is_fill(chunk):
                yield Substring(start, stop, chunk)
            start = stop

    @classmethod
    def from_substrings(cls, substrings):
        chunks = list(substring_chunks(substrings))
        return cls(chunks)


def substring_chunks(substrings, fill=FILL):
    previous = 0
    for index, substring in enumerate(substrings):
        if index > 0:
            size = substring.start - previous
            if size:
                yield fill * size
        yield substring.text
        previous = substring.stop


SEP = '|'
ESCAPE = [
    (SEP, r'\|'),
    ('\n', r'\n')
]


def escape_chunk(chunk):
    for source, target in ESCAPE:
        chunk = chunk.replace(source, target)
    return chunk


def parse_partition(line):
    chunks = line.split(SEP)
    return Partition(chunks)


def parse_partitions(lines):
    for line in lines:
        yield parse_partition(line)


def format_partition(partition):
    return SEP.join(escape_chunk(_) for _ in partition.chunks)


def format_partitions(partitions):
    for partition in partitions:
        yield format_partition(partition)


def update_partition(partition, segment):
    text = partition.text
    substrings = segment(text)
    return Partition.from_substrings(substrings)


def update_partitions(partitions, segment):
    for partition in partitions:
        yield update_partition(partition, segment)
