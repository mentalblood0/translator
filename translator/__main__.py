import argparse
import subprocess
import sys

from .Pdf import Pdf
from .Translator import Translator

parser = argparse.ArgumentParser(prog="Translator", description="Translate PDF and generate sentencewise table")
parser.add_argument("-e", "--extract-only", action="store_true", default=False)
parser.add_argument(
    "-l",
    "--language",
    default="ru",
    choices=subprocess.run(args=["trans", "-list-codes"], capture_output=True).stdout.decode().split("\n")[:-1],
)
parser.add_argument("-f", "--format", default="html", choices=["markdown", "html", "json"])
args = parser.parse_args()

pdf = Pdf(sys.stdin.buffer.read())
text = ". Footnotes. ".join(["".join(pdf.text), "".join(pdf.footnotes)])

if args.extract_only:
    result = text
else:
    translator = Translator(text, args.language)
    if args.format == "markdown":
        result = translator.markdown
    elif args.format == "html":
        result = translator.html
    else:
        result = translator.json

sys.stdout.write(result)
