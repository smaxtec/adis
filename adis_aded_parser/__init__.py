from .adis_file import AdisFile
from .adis_lines import (
    AdisLine,
    EndOfLogicalFileLine,
    PhysicalEndOfFileLine
)
import pprint

pp = pprint.PrettyPrinter(indent=2)

def parse(raw_input_text):
    raw_lines = split_lines(raw_input_text)
    lines = []
    for raw_line in raw_lines:
        if raw_line == "":
            continue
        lines.append(AdisLine.parse_line(raw_line))

    file = AdisFile.from_lines(lines)

    for block in file.get_blocks():
        print(block)

    pp.pprint(file.to_dict())


def split_lines(raw_input_text):
    # lines have to end with "\r\n" but we also accept lines that only end with "\n"
    lines = raw_input_text.split("\n")
    for line in lines:
        line = line.replace("\r", "")
    return lines
