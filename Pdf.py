import dataclasses
import functools
import pathlib
import re
import subprocess
import typing

import fitz


@dataclasses.dataclass
class Pdf:
    source: bytes

    @functools.cached_property
    def parsed(self):
        return fitz.open("pdf", self.source)

    def repeated(
        self,
        extract: typing.Callable[[fitz.Page], typing.Iterable[typing.Any]],
        key: typing.Callable[[typing.Any], typing.Any],
    ):
        Y: typing.Dict[float, int] = {}

        for p in self.parsed:
            for b in extract(p):
                y = key(b)
                if y not in Y:
                    Y[y] = 0
                Y[y] += 1

        return [*sorted(y for y, _ in sorted(Y.items(), key=lambda i: -i[1]))]

    @functools.cached_property
    def repeated_text_blocks(self):
        repeated = self.repeated(lambda p: p.get_text_blocks(), lambda b: b[1])
        return repeated[0], repeated[-1], repeated[-2]

    @functools.cached_property
    def repeated_drawings(self):
        return self.repeated(lambda p: p.get_drawings(), lambda d: (d["items"][0][1].y, d["items"][0][-1].y))

    @classmethod
    def footnotes_line_y(cls, p: fitz.Page) -> typing.Union[float, None]:
        drawings = p.get_drawings()
        if not drawings:
            return None
        footnotes_line = next(iter(p.get_drawings()))["items"][0]
        assert footnotes_line[0] == "l", "first drawing on page is not line"
        assert footnotes_line[1].y == footnotes_line[2].y, "first drawing on page is not horizontal line"
        return footnotes_line[1].y

    @functools.cached_property
    def tokens(self):
        for p in self.parsed:
            f = self.footnotes_line_y(p)
            for b in p.get_text_blocks():
                y = b[1]
                if y in self.repeated_text_blocks:
                    continue
                if f is not None and y > f:
                    yield "footnote", b[-3]
                else:
                    yield "text", b[-3]

    def _text(self, type: str):
        return (t[1] for t in self.tokens if t[0] == type)

    @property
    def text(self):
        return self._text("text")

    @property
    def footnotes(self):
        return self._text("footnote")
