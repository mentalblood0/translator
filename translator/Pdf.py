import dataclasses
import functools
import operator
import sys
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

        return [*sorted([y for y, _ in sorted(Y.items(), key=lambda i: -i[1])][:3])]

    @functools.cached_property
    def repeated_text_blocks(self):
        repeated = self.repeated(lambda p: p.get_text_blocks(), operator.itemgetter(1))
        return repeated[0], repeated[-1]

    @classmethod
    def footnotes_line_y(cls, p: fitz.Page) -> typing.Union[float, None]:
        drawings = p.get_drawings()
        sys.stderr.write(str(drawings) + "\n\n")
        if not drawings:
            return None
        result = None
        for d in p.get_drawings():
            lines = d["items"][0]
            if (lines[0] != "l") or (lines[1].y == lines[2].y):
                continue
            y = lines[1].y
            if (result is not None) and (y <= result):
                continue
            result = y
        return result

    @property
    def tokens(self):
        for p in self.parsed:
            f = self.footnotes_line_y(p)
            end = False
            for b in p.get_text_blocks():
                y = b[1]
                text = b[-3]
                if y in self.repeated_text_blocks:
                    continue
                if (f is not None) and (y > f):
                    yield "footnote", text
                elif not end:
                    if text.strip() == "References":
                        end = True
                        continue
                    yield "text", text
            if end:
                break

    def _text(self, token_type: str):
        return (t[1] for t in self.tokens if t[0] == token_type)

    @property
    def text(self):
        return self._text("text")

    @property
    def footnotes(self):
        return self._text("footnote")
