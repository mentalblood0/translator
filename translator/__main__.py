import argparse
import subprocess
import sys

from .Pdf import Pdf
from .Translator import Translator

parser = argparse.ArgumentParser(prog="Translator", description="Translate and generate sentencewise table")
subparsers = parser.add_subparsers(dest="subparser_name")

extract = subparsers.add_parser("extract")
extract.add_argument("-f", "--format", type=str, required=True, choices=["pdf"], help="Input format")

translate = subparsers.add_parser("translate")
translate.add_argument("-e", "--encoding", default="utf8", help="Input encoding")
translate.add_argument(
    "-l",
    "--language",
    default="ru",
    choices=subprocess.run(args=["trans", "-list-codes"], capture_output=True).stdout.decode().split("\n")[:-1],
    help="Target language",
)
translate.add_argument("-f", "--format", choices=["text", "markdown", "html", "json"], help="Output format")

args = parser.parse_args()

if args.subparser_name == "extract":
    if args.format == "pdf":
        pdf = Pdf(sys.stdin.buffer.read())
        for chunk in pdf.text:
            sys.stdout.write(chunk)
        sys.stdout.write(". Footnotes. ")
        for chunk in pdf.footnotes:
            sys.stdout.write(chunk)

elif args.subparser_name == "translate":
    translator = Translator(sys.stdin.buffer.read().decode(args.encoding), args.language)
    if args.format == "markdown":
        result = translator.markdown
    elif args.format == "html":
        result = translator.html
    elif args.format == "text":
        result = translator.text
    else:
        result = translator.json
    sys.stdout.write(result)
