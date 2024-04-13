import dataclasses
import functools
import json
import re
import subprocess
import typing


@dataclasses.dataclass
class Translator:
    source: str
    target_language: str

    @classmethod
    def filter(cls, s: str):
        return s.replace("-\n", "").replace("­\n", "").replace("\n", " ")

    @classmethod
    def split(cls, s: str):
        return (
            s[m.start() : m.end()]
            for m in re.finditer(
                r"(?:[^.?!]|(?:(?:Q|W|E|R|T|Y|U|I|O|P|A|S|D|F|G|H|J|K|L|Z|X|C|V|B|N|M)\.))*[^ .?!]{2,}(?:\.|!|\?)", s
            )
        )

    def _trans(self, sentences: typing.Iterable[str]):
        for r in (
            subprocess.run(
                args=("trans", f":{self.target_language}", "-e", "google", "--brief", "\n".join(sentences)),
                capture_output=True,
            )
            .stdout.decode()[:-1]
            .split("\n")
        ):
            yield r

    def trans(self, sentences: typing.Iterable[str]):
        buffer = []
        size = 0

        for s in sentences:
            buffer.append(s)
            size += len(s) + 1
            if size + len(s) >= 4096:
                for r in self._trans(buffer):
                    yield r
                buffer.clear()
                size = 0

        if buffer:
            for r in self._trans(buffer):
                yield r

    @property
    def sentences(self):
        return [*self.split(self.filter(self.source))]

    @functools.cached_property
    def translated(self):
        return [*zip(self.sentences, self.trans(self.sentences))]

    @property
    def markdown(self):
        return "|Оригинал|Перевод|\n|---|---|\n" + "\n".join(f"|{o}|{t}|" for o, t in self.translated)

    @property
    def html(self):
        return "".join(
            ["<table><thead><tr><th>Оригинал</th><th>Перевод</th></tr></thead><tbody>"]
            + [f"<tr><td>{o}</td><td>{t}</td></tr>" for o, t in self.translated]
            + ["</tbody></table>"]
        )

    @property
    def json(self):
        return json.dumps(self.translated)
