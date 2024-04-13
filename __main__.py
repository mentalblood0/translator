import argparse
import json
import sys

from .Pdf import Pdf
from .Translator import Translator

parser = argparse.ArgumentParser(prog="Translator", description="Translate PDF and generate sentencewise table")
parser.add_argument("-f", "--format", required=True)
parser.add_argument("-l", "--language", required=True)
args = parser.parse_args()

pdf = Pdf(sys.stdin.buffer.read())
translator = Translator(".\n".join(["".join(pdf.text), "".join(pdf.footnotes)]), args.language)

if args.format == "markdown":
    print(translator.markdown)
elif args.format == "html":
    print(translator.html)
elif args.format == "json":
    print(json.dumps(translator.translated))
