import pprint
from .item_field_parser import ItemFieldParser

pp = pprint.PrettyPrinter(indent=2)

STRICT_MODE = False

def parse(raw_input_text):
    raw_lines = split_lines(raw_input_text)
    # print(lines)
    lines = []
    for raw_line in raw_lines:
        if raw_line == "":
            continue
        lines.append(Line.parse_line(raw_line))
    
    # pp.pprint(lines)
    item_parsers = []
    for line in lines:
        if type(line) == DefinitionLine:
            print("Found definition")
            item_parsers = line.get_item_parsers()
        if type(line) == ValueLine:
            items = line.parse(item_parsers)
            pp.pprint(items)
        if type(line) == PhysicalEndOfFile:
            break

    

def split_lines(raw_input_text):
    # lines have to end with "\r\n" but we also accept lines that only end with "\n"
    lines = raw_input_text.split("\n")
    for line in lines:
        line = line.replace("\r", "")
    return lines


class Line:
    # takes the line without the first char
    def __init__(self, line):
        self.line = line
        self.line_type_char = line[0]
        self.status_symbol = line[1]

        status_symbols = {
            "H": "header",
            "N": "normal",
            "S": "synchronisation",
            "F": "faulty",
            "D": "deletion"
        }

        self.status = status_symbols[self.status_symbol]

        if not self.status_allowed(self.status):
            raise Exception(
                f"Linetype {self.line_type} may not have status {self.status}")

    # has to be implemented by the derived classes
    def status_allowed(self, status):
        return status in self.allowed_statuses

    def get_type_char(self):
        return self.line_type_char

    def __repr__(self):
        return "%s status: %s, line: %s" % (self.line_type, self.status, self.line)
    

    @staticmethod
    def parse_line(line):
        line_type_parsers = {
            "D": DefinitionLine,
            "V": ValueLine,
            "E": EndOfLogicalFileLine,
            "C": CommentLine,
            "Z": PhysicalEndOfFile
        }

        line_type = line[0]
        return line_type_parsers[line_type](line)


class DefinitionLine(Line):
    def __init__(self, line):
        self.line_type = "Definition"
        self.allowed_statuses = [
            "header", "normal", "synchronisation", "faulty", "deletion"
        ]
        super().__init__(line)

        self.entity_number = self.line[2:8]

        item_definition_text = self.line[8:]
        item_definition_blocks = self.split_item_definition_text(item_definition_text)

        self.item_parsers = []
        for item_definition_block in item_definition_blocks:
            self.item_parsers.append(self.create_item_parser(item_definition_block))

    def get_item_parsers(self):
        return self.item_parsers

    def split_item_definition_text(self, item_definition_text):
        definition_block_length = 11    # each item definition consists of 11 chars
        if len(item_definition_text) % definition_block_length != 0:
            raise Exception("Length of definitions text is %d but it has to be a multiple of %d"
                % (len(item_definition_text), definition_block_length))
        definition_blocks = []
        number_of_item_definitions = int(len(item_definition_text) / definition_block_length)
        for block_count in range(number_of_item_definitions):
            start_index = block_count * definition_block_length
            end_index = start_index + definition_block_length
            definition_blocks.append(item_definition_text[start_index:end_index])
        return definition_blocks

    def create_item_parser(self, header_part):
        delimitor = header_part[0:2]
        if delimitor != "00":
            raise Exception("Delimitor \"%s\" is different than \"00\"" % delimitor)

        item_number = header_part[2:8]
        field_size = header_part[8:10]
        decimal_digits = header_part[10]
        return ItemFieldParser(item_number, field_size, decimal_digits)


class ValueLine(Line):
    def __init__(self, line):
        self.line_type = "Value"
        self.allowed_statuses = [
            "header", "normal", "synchronisation", "faulty", "deletion"
        ]
        super().__init__(line)

        self.entity_number = self.line[2:8]
        self.raw_items = self.line[8:]

    def parse(self, item_parsers):
        expected_raw_items_length = 0
        for item_parser in item_parsers:
            expected_raw_items_length += item_parser.get_field_size()
        
        if len(self.raw_items) != expected_raw_items_length:
            expected_raw_items_length_when_last_item_empty = \
                expected_raw_items_length - item_parsers[-1].get_field_size()
            if STRICT_MODE:
                raise Exception("""Expecting an item text length of %d, but got %d chars.
                    Turning strict mode off might fix this problem."""
                    % (expected_raw_items_length, len(self.raw_items)))
            elif len(self.raw_items) < expected_raw_items_length_when_last_item_empty:
                raise Exception("""Expecting an item text length of %d chars or %d chars,
                    but got %d chars."""
                    % (expected_raw_items_length, 
                        expected_raw_items_length_when_last_item_empty,
                        len(self.raw_items)))

        items = []
        current_position = 0
        for item_parser in item_parsers:
            field_size = item_parser.get_field_size()
            items.append(item_parser.parse_at_position(self.raw_items, current_position))
            current_position += field_size

        return items


class EndOfLogicalFileLine(Line):
    def __init__(self, line):
        self.line_type = "End of logical file"
        self.allowed_statuses = ["normal"]
        super().__init__(line)


class CommentLine(Line):
    def __init__(self, line):
        self.line_type = "Comment"
        self.allowed_statuses = [
            "header", "normal", "synchronisation", "faulty", "deletion"
        ]
        super().__init__(line)

        self.comment = self.line[2:]
    
    def get_comment(self):
        return self.comment


class PhysicalEndOfFile(Line):
    def __init__(self, line):
        self.line_type = "Physical end of file"
        self.allowed_statuses = ["normal"]
        super().__init__(line)
