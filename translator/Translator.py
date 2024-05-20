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
        yield from (
            subprocess.run(
                args=("trans", f":{self.target_language}", "-e", "google", "--brief", "\n".join(sentences)),
                capture_output=True,
            )
            .stdout.decode()[:-1]
            .split("\n")
        )

    def trans(self, sentences: typing.Iterable[str]):
        buffer = []
        size = 0

        for s in sentences:
            buffer.append(s)
            size += len(s) + 1
            if size + len(s) >= 4096:
                yield from self._trans(buffer)
                buffer.clear()
                size = 0

        if buffer:
            yield from self._trans(buffer)

    @functools.cached_property
    def sentences(self):
        return [*self.split(self.filter(self.source))]

    @functools.cached_property
    def translated(self):
        return zip(self.sentences, self.trans(self.sentences))

    @functools.cached_property
    def headers(self):
        t = [*self.trans(["Source", "The translate"])]
        return t[0], t[1]

    @functools.cached_property
    def text(self):
        return "\n\n".join("\n".join([o, t]) for o, t in self.translated)

    @property
    def markdown(self):
        return f"|{self.headers[0]}|{self.headers[1]}|\n|---|---|\n" + "\n".join(
            f"|{o}|{t}|" for o, t in self.translated
        )

    @property
    def html(self):
        return "".join(
            [f"<table><thead><tr><th>{self.headers[0]}</th><th>{self.headers[1]}</th></tr></thead><tbody>"]
            + [f"<tr><td>{o}</td><td>{t}</td></tr>" for o, t in self.translated]
            + ["</tbody></table>"]
        )

    @property
    def json(self):
        return json.dumps(self.translated)
