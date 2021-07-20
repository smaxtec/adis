from .adis_field_definition import AdisFieldDefinition

class AdisLine:
    status_chars = {
        "H": "header",
        "N": "normal",
        "S": "synchronisation",
        "F": "faulty",
        "D": "deletion"
    }

    # takes the line without the first char
    def __init__(self, line):
        self.line = line
        self.line_type_char = line[0]
        self.status_char = line[1]

        self.status = AdisLine.status_chars[self.status_char]

        if not self.status_allowed(self.status):
            raise Exception(
                f"Linetype {self.line_type} may not have status {self.status}")

    def status_allowed(self, status):
        return status in self.allowed_statuses

    def get_type_char(self):
        return self.line_type_char

    def get_status_char(self):
        return self.status_char

    def __repr__(self):
        return "%s status: %s, line: %s" % (self.line_type, self.status, self.line)
    
    @staticmethod
    def parse_line(line):
        line_types = {
            "D": DefinitionLine,
            "V": ValueLine,
            "E": EndOfLogicalFileLine,
            "C": CommentLine,
            "Z": PhysicalEndOfFileLine
        }

        line_type = line[0]
        return line_types[line_type](line)


class DefinitionLine(AdisLine):
    def __init__(self, line):
        self.line_type = "Definition"
        self.allowed_statuses = [
            "header", "normal", "synchronisation", "faulty", "deletion"
        ]
        super().__init__(line)

        self.entity_number = self.line[2:8]

        field_definitions_text = self.line[8:]
        field_definition_blocks = self.split_field_definitions_text(field_definitions_text)

        self.field_definitions = []
        for field_definition_block in field_definition_blocks:
            self.field_definitions.append(self.create_field_definition(field_definition_block))

    def get_entity_number(self):
        return self.entity_number

    def get_field_definitions(self):
        return self.field_definitions

    def split_field_definitions_text(self, field_definitions_text):
        definition_block_length = 11    # each field definition consists of 11 chars
        if len(field_definitions_text) % definition_block_length != 0:
            raise Exception("Length of definitions text is %d but it has to be a multiple of %d"
                % (len(field_definitions_text), definition_block_length))
        definition_blocks = []
        number_of_field_definitions = int(len(field_definitions_text) / definition_block_length)
        for block_count in range(number_of_field_definitions):
            start_index = block_count * definition_block_length
            end_index = start_index + definition_block_length
            definition_blocks.append(field_definitions_text[start_index:end_index])
        return definition_blocks

    def create_field_definition(self, header_part):
        item_number = header_part[0:8]
        field_size = header_part[8:10]
        decimal_digits = header_part[10]
        return AdisFieldDefinition(item_number, field_size, decimal_digits)


class ValueLine(AdisLine):
    def __init__(self, line):
        self.line_type = "Value"
        self.allowed_statuses = [
            "header", "normal", "synchronisation", "faulty", "deletion"
        ]
        super().__init__(line)

        self.entity_number = self.line[2:8]
        self.raw_items = self.line[8:]

    def get_entity_number(self):
        return self.entity_number

    def parse(self, field_definitions):
        expected_raw_items_length = 0
        for field_definition in field_definitions:
            expected_raw_items_length += field_definition.get_field_size()
        
        if len(self.raw_items) != expected_raw_items_length:
            expected_raw_items_length_when_last_item_empty = \
                expected_raw_items_length - field_definitions[-1].get_field_size()
            if len(self.raw_items) < expected_raw_items_length_when_last_item_empty:
                raise Exception("""Expecting an item text length of %d chars or %d chars,
                    but got %d chars."""
                    % (expected_raw_items_length, 
                        expected_raw_items_length_when_last_item_empty,
                        len(self.raw_items)))

        values = []
        current_position = 0
        for field_definition in field_definitions:
            field_size = field_definition.get_field_size()
            value = field_definition.parse_field_at_position(self.raw_items, current_position)
            if value is not None:
                values.append(value)
            current_position += field_size

        return values


class EndOfLogicalFileLine(AdisLine):
    def __init__(self, line):
        self.line_type = "End of logical file"
        self.allowed_statuses = ["normal"]
        super().__init__(line)


class CommentLine(AdisLine):
    def __init__(self, line):
        self.line_type = "Comment"
        self.allowed_statuses = [
            "header", "normal", "synchronisation", "faulty", "deletion"
        ]
        super().__init__(line)
        self.comment = self.line[2:]
    
    def get_comment(self):
        return self.comment


class PhysicalEndOfFileLine(AdisLine):
    def __init__(self, line):
        self.line_type = "Physical end of file"
        self.allowed_statuses = ["normal"]
        super().__init__(line)
