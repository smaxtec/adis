from .adis_lines import (
    AdisLine,
    DefinitionLine,
    ValueLine
)

"""
An AdisBlock consists of one definition and (one or) multiple values.
"""

class AdisBlock:
    def __init__(self, status, entity_number, field_definitions, data_rows):
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
        return self.entity_number

    def get_field_definitions(self):
        return self.field_definitions
    
    def get_data_rows(self):
        return self.data_rows

    @staticmethod
    def from_lines(lines):
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

        return AdisBlock(status, entity_number, field_definitions, data_rows)

    def to_dict(self):
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
        data_row_dict = {}
        for value in data_row:
            value_as_dict = value.to_dict()
            data_row_dict[value_as_dict["item_number"]] = value_as_dict["value"]
        return data_row_dict

    def dumps_definitions(self):
        text = "D" + self.status + self.entity_number
        for definition in self.field_definitions:
            text += definition.dumps()
        text += "\r\n"
        return text

    def dumps_data(self):
        text = ""
        for data_row in self.data_rows:
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
        text = self.dumps_definitions()
        text += self.dumps_data()
        return text

    def __repr__(self):
        return "AdisBlock with status=%s and entity_number=%s containing %d data row(s)" \
                % (self.status, self.entity_number, len(self.data_rows))
