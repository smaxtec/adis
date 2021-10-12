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
        """Creates an AdisLine.

        Args:
            line (string): the raw line from the ADIS file
        """
        self.line = line
        self.line_type_char = line[0]
        self.status_char = line[1]

        self.status = AdisLine.status_chars[self.status_char]

        if not self.status_allowed(self.status):
            raise Exception(
                f"Linetype {self.line_type} may not have status {self.status}")

    def status_allowed(self, status):
        """Returns whether the given status is allowed for this AdisLine or not.

        Args:
            status (string): status char

        Returns:
            boolean: True if this status is allowed for this line, otherwise False
        """
        return status in self.allowed_statuses

    def get_type_char(self):
        """Returns the type char of this AdisLine.

        Returns:
            string: type char of this AdisLine
        """
        return self.line_type_char

    def get_status_char(self):
        """Returns the status char of this AdisLine.

        Returns:
            string: status char of this AdisLine
        """
        return self.status_char

    def __repr__(self):
        return "%s status: %s, line: %s" % (self.line_type, self.status, self.line)
    
    @staticmethod
    def parse_line(line):
        """Creates an AdisLine from the given line.

        Args:
            line (string): line from the ADIS file

        Returns:
            AdisLine: new AdisLine
        """
        line_types = {
            "D": DefinitionLine,
            "V": ValueLine,
            "E": EndOfLogicalFileLine,
            "C": CommentLine,
            "Z": PhysicalEndOfFileLine,
            "T": PhysicalEndOfFileLine
        }

        line_type = line[0]
        return line_types[line_type](line)


class DefinitionLine(AdisLine):
    def __init__(self, line):
        """Creates a DefinitionLine

        Args:
            line (string): line from ADIS file
        """
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
        """Returns the entity number.

        Returns:
            string: entity number if this line
        """
        return self.entity_number

    def get_field_definitions(self):
        """returns the field definitions.

        Returns:
            list[AdisFieldDefinition]: list of field definitions
        """
        return self.field_definitions

    def split_field_definitions_text(self, field_definitions_text):
        """Splits the part of an ADIS file line that contains the field definitions into parts. \
            (Each field definition is one part)

        Args:
            field_definitions_text (string): part of a raw ADIS line that holds the field \
                definitions

        Returns:
            list[string]: list that holds the different field definition strings
        """
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

    def create_field_definition(self, field_definition_block):
        """Creates an AdisFieldDefinition from the raw definition block from the ADIS line.

        Args:
            field_definition_block (string): part of the raw ADIS line that holds a field \
                definition

        Returns:
            AdisFieldDefinition: new AdisFieldDefinition
        """
        item_number = field_definition_block[0:8]
        field_size = field_definition_block[8:10]
        decimal_digits = field_definition_block[10]
        return AdisFieldDefinition(item_number, field_size, decimal_digits)


class ValueLine(AdisLine):
    def __init__(self, line):
        """Creates a ValueLine.

        Args:
            line (string): raw line from an ADIS file
        """
        self.line_type = "Value"
        self.allowed_statuses = [
            "header", "normal", "synchronisation", "faulty", "deletion"
        ]
        super().__init__(line)

        self.entity_number = self.line[2:8]
        self.raw_items = self.line[8:]

    def get_entity_number(self):
        """Returns the entity number.

        Returns:
            string: entity number if this line
        """
        return self.entity_number

    def parse(self, field_definitions):
        """Parses a list of AdisValues from a raw ADIS file value line using the provided \
            list of field definitions.

        Args:
            field_definitions (list[AdisFieldDefinition]): The field definitions for the fields \
                in this line.

        Returns:
            list[AdisValue]: AdisValues parsed from this line
        """
        expected_raw_items_length = 0
        for field_definition in field_definitions:
            expected_raw_items_length += field_definition.get_field_size()
        
        if len(self.raw_items) != expected_raw_items_length:
            expected_raw_items_length_when_last_item_empty = \
                expected_raw_items_length - field_definitions[-1].get_field_size()
            if len(self.raw_items) < expected_raw_items_length_when_last_item_empty:
                raise Exception("Expecting an item text length of %d chars or %d chars, " \
                    "but got %d chars."
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
        """Creates an EndOfLogicalFileLine. Note that each physical ADIS file can contain \
            multiple logical files.

        Args:
            line (string): raw line from an ADIS file
        """
        self.line_type = "End of logical file"
        self.allowed_statuses = ["normal"]
        super().__init__(line)


class CommentLine(AdisLine):
    def __init__(self, line):
        """Creates a CommentLine

        Args:
            line (string): raw line from an ADIS file
        """
        self.line_type = "Comment"
        self.allowed_statuses = [
            "header", "normal", "synchronisation", "faulty", "deletion"
        ]
        super().__init__(line)
        self.comment = self.line[2:]
    
    def get_comment(self):
        """Returns the comment.

        Returns:
            string: comment
        """
        return self.comment


class PhysicalEndOfFileLine(AdisLine):
    def __init__(self, line):
        """Creates a PhysicalEndOfFileLine.

        Args:
            line (string): raw line from an ADIS file
        """
        self.line_type = "Physical end of file"
        self.allowed_statuses = ["normal"]
        super().__init__(line)
