from .adis_lines import (
    DefinitionLine,
    ValueLine
)

import pprint

pp = pprint.PrettyPrinter(indent=2)

"""
An AdisBlock consists of one definition and (one or) multiple values.
"""

class AdisBlock:
    def __init__(self, entity_number, field_definitions, data_rows):
        self.entity_number = entity_number
        self.field_definitions = field_definitions
        self.data_rows = data_rows

    def get_entity_number(self):
        return self.entity_number

    def get_field_definitions(self):
        return self.field_definitions
    
    def get_data_rows(self):
        return self.data_rows

    @staticmethod
    def from_lines(lines):
        entity_number = None
        field_definitions = None
        data_rows = []
        for line in lines:
            if type(line) == DefinitionLine:
                entity_number = line.get_entity_number()
                field_definitions = line.get_field_definitions()
            if type(line) == ValueLine:
                if field_definitions is None:
                    raise Exception("Definition line is missing before value line")
                data_rows.append(line.parse(field_definitions))

        if entity_number is None or field_definitions is None:
            raise Exception("Definition is missing.")

        return AdisBlock(entity_number, field_definitions, data_rows)

    def to_dict(self):
        result_dict = {
            "definitions": [],
            "data": []
        }
        for definition in self.field_definitions:
            result_dict["definitions"].append(definition.to_dict())

        for data_row in self.data_rows:
            data_row_content_as_dict = {}
            for value in data_row:
                value_as_dict = value.to_dict()
                data_row_content_as_dict[value_as_dict["item_number"]] = value_as_dict["value"]
            result_dict["data"].append(data_row_content_as_dict)

        return result_dict

    def __repr__(self):
        return "AdisBlock containing %d data row(s)" % len(self.data_rows)
