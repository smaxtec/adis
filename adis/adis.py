import json
from .adis_file import AdisFile
from .adis_lines import (
    AdisLine,
    EndOfLogicalFileLine,
    PhysicalEndOfFileLine
)
from .adis_value import AdisValue

def split_lines(raw_input_text):
    """Splits the provided text into lines. Lines are splitted at "\n" and "\r" chars get \
        removed as well.

    Args:
        raw_input_text (string): ADIS text

    Returns:
        list: lines of the provided ADIS text
    """
    # lines have to end with "\r\n" but we also accept lines that only end with "\n"
    lines = []
    for raw_line in raw_input_text.split("\n"):
        lines.append(raw_line.replace("\r", ""))    # remove \r
    return lines


class Adis:
    def __init__(self, adis_files):
        """Creates an Adis object based on the logical ADIS files

        Args:
            adis_files (list[AdisFile]): List of logical ADIS files
        """
        self.files = adis_files

    def get_files(self):
        """Returns a list containing the logical AdisFiles

        Returns:
            list[AdisFile]: list containing the logical AdisFiles
        """
        return self.files

    @staticmethod
    def parse(text):
        """This method parses the provided ADIS text into an Adis object.

        Args:
            text (string): ADIS file content

        Returns:
            Adis: Adis object created from the provided ADIS text
        """
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
        """This method parses the given ADIS file to an Adis object.

        Args:
            path_to_file (string): Path to the ADIS file

        Returns:
            Adis: Adis object created from the provided ADIS file
        """
        with open(path_to_file, "r") as input_file:
            text = input_file.read()
        return Adis.parse(text)

    def get_list(self, strip_string_values=True):
        """Returns a list containing of the logical ADIS files and their contents. \
            The returned list only contains builtin types.

        Args:
            strip_string_values (bool, optional, by default True): Whether string \
                values should be stripped or not.

        Returns:
            list: containing the logical adis files and their contents as builtin types.
        """

        AdisValue.strip_string_values = strip_string_values
        list_of_files = []
        for adis_file in self.files:
            list_of_files.append(adis_file.to_dict())
        return list_of_files

    def to_json(self, strip_string_values=True, mapping_dict: dict=None):
        """Creates a json from the Adis object.

        Args:
            strip_string_values (bool, optional, by default True): Whether string \
                values should be stripped or not.
            mapping_dict (dict): Optional dictionary of mapping values \
                for entity numbers (e.g. {"0080004": "Betriebsnummer"})

        Returns:
            string: Adis as json
        """
        if mapping_dict is None or type(mapping_dict) != dict:
            return json.dumps(self.get_list(strip_string_values))
        else:
            list_of_adis = self.get_list(strip_string_values)
            return json.dumps(self.add_string_value(list_of_adis, mapping_dict))

    @staticmethod
    def from_json(json_text):
        """Creates an Adis object based on the provided json.

        Args:
            json_text (string): json text. Note that the json has to have a specific structure. \
                Take a look at the README for more information.

        Returns:
            Adis: Adis object
        """
        data = json.loads(json_text)
        if type(data) is not list:
            raise Exception("""The root element of the JSON has to be a list. Got %s."""
                            % type(data))
        adis_files = []
        for file_dict in data:
            if type(file_dict) is not dict:
                raise Exception("Expecting a dict but got %s." % type(file_dict))
            adis_files.append(AdisFile.from_dict(file_dict))

        return Adis(adis_files)

    @staticmethod
    def from_json_file(path_to_json_file):
        """Creates an Adis object based on the provided json file.

        Args:
            path_to_json_file (string): Path to the json file. Note that the json has to have a \
                specific structure. Take a look at the README for more information.

        Returns:
            Adis: Adis object
        """
        with open(path_to_json_file) as input_file:
            raw_content = input_file.read()
        return Adis.from_json(raw_content)

    def dumps(self):
        """Creates an ADIS text

        Returns:
            string: ADIS text
        """
        file_texts = []
        for adis_file in self.files:
            file_texts.append(adis_file.dumps())
        
        end_of_logical_file_line = "EN\r\n"
        text = end_of_logical_file_line.join(file_texts)

        text += "ZN\r\n"    # physical end of file
        return text

    def __repr__(self):
        return """Adis containing %d Adis-files""" % len(self.files)

    @staticmethod
    def add_string_value(obj: list, entity_data_dict: dict):
        """ Adds string value to definition list

        Args:
            obj (list): containing the logical adis files and their contents as builtin types without string values
            entity_data_dict (dict): dictionary of mapping values for \
             item numbers (e.g. {"0080004": "Betriebsnummer"})

        Returns:
             list: containing the logical adis files and their contents as builtin types with string values

        """
        for o in obj:
            for defs in o:
                for items in obj[0].get(defs).get("definitions"):
                    x = entity_data_dict.get(items['item_number'][2:], items['item_number'][2:])
                    items['item_name'] = x
        return obj
