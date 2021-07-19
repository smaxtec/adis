from .adis_value import AdisValue

class AdisFieldDefinition:
    def __init__(self, item_number, field_size, decimal_digits):
        self.item_number = item_number
        self.field_size = int(field_size)
        self.decimal_digits = int(decimal_digits)

    def get_field_size(self):
        return self.field_size

    def parse_field_at_position(self, raw_text, position):
        # return a string when decimal_digits is 0 / otherwise float
        item_number = self.item_number
        value = raw_text[position:position + self.field_size]

        value_size = len(value)
        if value_size != 0 and value_size != self.field_size:
            raise Exception("""Expected field size of %d chars or an empty field, but got
                field size of %d chars.""" % (self.field_size, value_size))
        elif value_size == 0:
            value = None

        if value is not None and \
            (self.only_contains_char(value, "?") or     # null value field
            self.only_contains_char(value, "|")):       # undefined DDI number
            value = None

        # handle case where it's a decimal number
        if value is not None and self.decimal_digits != 0:
            value = self.parse_number(value)
            value /= 10**self.decimal_digits

        return AdisValue(item_number, value)

    def parse_number(self, text):
        return float(text.replace(" ", ""))

    def only_contains_char(self, text, allowed_char):
        for char in text:
            if char != allowed_char:
                return False
        return True

    def to_dict(self):
        return {
            "item_number": self.item_number,
            "field_size": self.field_size,
            "decimal_digits": self.decimal_digits
        }

    def __repr__(self):
        return "AdisFieldDefinition: item_number=%s, field_size=%d, decimal_digits=%d" \
            % (self.item_number, self.field_size, self.decimal_digits)
