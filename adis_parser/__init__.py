import json
from .adis_file import AdisFile
from .adis_lines import (
    AdisLine,
    EndOfLogicalFileLine,
    PhysicalEndOfFileLine
)

def split_lines(raw_input_text):
    # lines have to end with "\r\n" but we also accept lines that only end with "\n"
    lines = []
    for raw_line in raw_input_text.split("\n"):
        lines.append(raw_line.replace("\r", ""))    # remove \r
    return lines


class Adis:
    def __init__(self, adis_files):
        self.files = adis_files

    @staticmethod
    def parse(text):
        raw_lines = split_lines(text)

        adis_files = []

        lines_for_file = []
        for raw_line in raw_lines:
            if raw_line == "":
                continue
            
            line = AdisLine.parse_line(raw_line)
            if type(line) == EndOfLogicalFileLine or type(line) == PhysicalEndOfFileLine:
                adis_files.append(AdisFile.from_lines(lines_for_file))
                lines_for_file = []
            else:
                lines_for_file.append(line)

        return Adis(adis_files)

    @staticmethod
    def parse_from_file(path_to_file):
        with open(path_to_file, "r") as input_file:
            text = input_file.read()
        return Adis.parse(text)

    def get_list(self):
        list_of_files = []
        for adis_file in self.files:
            list_of_files.append(adis_file.to_dict())
        return list_of_files

    def to_json(self):
        return json.dumps(self.get_list())

    @staticmethod
    def from_json(json_text):
        data = json.loads(json_text)
        if type(data) is not list:
            raise Exception("""The root element of the JSON has to be a list. Got %s."""
                            % type(data))
        adis_files = []
        for file_dict in data:
            if type(file_dict) is not dict:
                raise Exception("Expecting a dict but got %s." % type(raw_file))
            adis_files.append(AdisFile.from_dict(file_dict))

        return Adis(adis_files)

    def from_json_file(path_to_json_file):
        with open(path_to_json_file) as input_file:
            raw_content = input_file.read()
        return Adis.from_json(raw_content)

    def dumps(self):
        file_texts = []
        for adis_file in self.files:
            file_texts.append(adis_file.dumps())
        
        end_of_logical_file_line = "EN\r\n"
        text = end_of_logical_file_line.join(file_texts)

        text += "ZN\r\n"    # physical end of file
        return text

    def __repr__(self):
        return """Adis containing %d Adis-files""" % len(self.files)
