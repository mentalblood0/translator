import argparse
import sys

from .Pdf import Pdf
from .Translator import Translator

parser = argparse.ArgumentParser(prog="Translator", description="Translate PDF and generate sentencewise table")
parser.add_argument("-f", "--format", required=True, choices=["markdown", "html", "json"])
parser.add_argument("-l", "--language", required=True)
args = parser.parse_args()

pdf = Pdf(sys.stdin.buffer.read())
translator = Translator(". ".join(["".join(pdf.text), "".join(pdf.footnotes)]), args.language)

if args.format == "markdown":
    result = translator.markdown
elif args.format == "html":
    result = translator.html
result = translator.json

sys.stdout.write(result)