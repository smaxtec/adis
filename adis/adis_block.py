from .adis_field_definition import AdisFieldDefinition
from .adis_lines import (
    AdisLine,
    DefinitionLine,
    ValueLine
)
from .adis_value import AdisValue

"""
An AdisBlock consists of one definition and (one or) multiple data rows.
Each data row has multiple fields.
"""

class AdisBlock:
    def __init__(self, entity_number, status, field_definitions, data_rows):
        """Creates an AdisBlock object.

        Args:
            entity_number (string): Entity number of this Block (has to be a string with 6 chars)
            status (string): Status char of this block, can be H, N, S, F or D
            field_definintions (list[AdisFieldDefinition]): Field definitions
            data_rows (list[list[AdisValue]]): list of data rows, each data row is a list \
                containing AdisValue
        """
        if len(status) != 1:
            raise Exception("Status may only be one char.")
        if status not in AdisLine.status_chars:
            raise Exception("Invalid status char. Has to be one of %s."
                % AdisLine.status_chars)
        if type(entity_number) is not str or len(entity_number) != 6:
            raise Exception("""The entity number has to be a string consisting of 6 chars.
                Got \"%s\".""" % entity_number)
        self.status = status
        self.entity_number = entity_number
        self.field_definitions = field_definitions
        self.data_rows = data_rows

    def get_entity_number(self):
        """Returns the entity number of this block.

        Returns:
            string: Entity number of this block (is a string of 6 chars)
        """
        return self.entity_number

    def get_field_definitions(self):
        """Returns the field definitions of this block.

        Returns:
            list[AdisFieldDefinition]: list containing field definitions
        """
        return self.field_definitions
    
    def get_data_rows(self):
        """Returns the data rows of this block.

        Returns:
            list[list[AdisValue]]: list of data rows. Each row is a list of AdisValues
        """
        return self.data_rows

    @staticmethod
    def from_lines(lines):
        """Creates an AdisBlock from a list of AdisLines

        Args:
            lines (list[AdisLine]): list of AdisLines
        
        Returns:
            AdisBlock: new AdisBlock
        """
        status = None
        entity_number = None
        field_definitions = None
        data_rows = []
        for line in lines:
            if type(line) == DefinitionLine:
                status = line.get_status_char()
                entity_number = line.get_entity_number()
                field_definitions = line.get_field_definitions()
            if type(line) == ValueLine:
                if field_definitions is None:
                    raise Exception("Definition line is missing before value line")
                data_rows.append(line.parse(field_definitions))

        if entity_number is None or field_definitions is None:
            raise Exception("Definition is missing.")

        return AdisBlock(entity_number, status, field_definitions, data_rows)

    @staticmethod
    def from_dict(entity_number, block_dict):
        """Creates an AdisBlock form a dict.

        Args:
            entity_number (string): Entity number of the block
            block_dict (dict): containing the data rows, the field definitions and the status

        Returns:
            AdisBlock: new AdisBlock
        """
        if "status" not in block_dict:
            raise Exception("\"status\" field is missing in block dict.")
        if "definitions" not in block_dict:
            raise Exception("\"definitions\" field is missing in block dict.")
        if "data" not in block_dict:
            raise Exception("\"data\" field is missing in block dict.")

        status = block_dict["status"]
        field_definitions = []
        for definition_dict in block_dict["definitions"]:
            if type(definition_dict) is not dict:
                raise Exception("A field definition has to be a dict but got %s."
                                % type(definition_dict))
            definition = AdisFieldDefinition.from_dict(definition_dict)
            field_definitions.append(definition)

        if type(block_dict["data"]) is not list:
            raise Exception("The data of each block has to be a list. Got %s."
                            % type(block_dict["data"]))
        
        data_rows = []
        for data_row_dict in block_dict["data"]:
            if type(data_row_dict) is not dict:
                raise Exception("Each data row has to be a dict. Got %s."
                                % type(data_row_dict))
            data_row = []
            for definition in field_definitions:
                item_number = definition.get_item_number()
                if item_number in data_row_dict:
                    value = data_row_dict[item_number]
                    adis_value = AdisValue(item_number, value)
                    data_row.append(adis_value)

            data_rows.append(data_row)

        return AdisBlock(entity_number, status, field_definitions, data_rows)

    def to_dict(self):
        """Creates a dict cointaining all data of this block

        Returns:
            dict: contains the field definitions, the data rows and the status of the block
        """
        result_dict = {
            "definitions": [],
            "data": [],
            "status": self.status
        }
        for definition in self.field_definitions:
            result_dict["definitions"].append(definition.to_dict())

        for data_row in self.data_rows:
            result_dict["data"].append(self.data_row_to_dict(data_row))

        return result_dict

    def data_row_to_dict(self, data_row):
        """Turns a data row to a dict.

        Args:
            data_row (list[AdisValue]): list containing the values of the data row

        Returns:
            dict: dict where the key is the item number and the value is the actual value of the \
                field
        """
        data_row_dict = {}
        for value in data_row:
            value_as_dict = value.to_dict()
            data_row_dict[value_as_dict["item_number"]] = value_as_dict["value"]
        return data_row_dict

    def dumps_definitions(self):
        """Creats a ADIS definition line string from the field definitions.

        Returns:
            string: ADIS definition line string
        """
        text = "D" + self.status + self.entity_number
        for definition in self.field_definitions:
            text += definition.dumps()
        text += "\r\n"
        return text

    def dumps_data(self):
        """Turns the data rows into value lines.

        Returns:
            string: value lines
        """
        text = ""
        for data_row in self.data_rows:
            # create a value line
            text += "V" + self.status + self.entity_number
            data_row_dict = self.data_row_to_dict(data_row)
            for definition in self.field_definitions:
                item_number = definition.get_item_number()
                if item_number not in data_row_dict:
                    # the value of this field is undefined
                    text += definition.dumps_value(None, undefined=True)
                else:
                    value = data_row_dict[item_number]
                    text += definition.dumps_value(value)
            
            text += "\r\n"
        return text

    def dumps(self):
        """Creates an ADIS text form this block.

        Returns:
            string: ADIS text of this block
        """
        text = self.dumps_definitions()
        text += self.dumps_data()
        return text

    def __repr__(self):
        return "AdisBlock with status=%s and entity_number=%s containing %d data row(s)" \
                % (self.status, self.entity_number, len(self.data_rows))
