from .adis_value import AdisValue

class AdisFieldDefinition:
    def __init__(self, item_number, field_size, decimal_digits):
        if type(item_number) is not str or len(item_number) != 8:
            raise Exception("The item_number has to be a string with length = 8. Got \"%s\""
                % item_number)
        self.item_number = item_number
        
        self.field_size = int(field_size)
        if self.field_size < 1 or 99 < self.field_size:
            raise Exception("The field size has to be a number between 1 and 99. Got %d."
                % self.field_size)
        
        self.decimal_digits = int(decimal_digits)
        if self.decimal_digits < 0 or 9 < self.decimal_digits:
            raise Exception("""The number of decimal digits has to be a number between 0 and 9.
                Got %d.""" % self.decimal_digits)

    def get_item_number(self):
        return self.item_number

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

        if value is not None and self.only_contains_char(value, "?"):   # null value field
            value = None

        if value is not None and self.only_contains_char(value, "|"):   # undefined DDI number
            return None         # no value will be created for this field

        # handle case where it's a decimal number
        if value is not None and self.decimal_digits != 0:
            value = float(value)
            value /= 10**self.decimal_digits

        return AdisValue(item_number, value)

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

    def dumps(self):
        text = self.item_number
        text += self.number_to_str_with_window_size(self.field_size, 2)
        text += str(self.decimal_digits)    # only 1 char window
        return text

    def dumps_value(self, value, undefined=False):
        if undefined:
            return self.field_size * "|"
        if value is None:
            return self.field_size * "?"
        elif type(value) is str:
            if self.field_size < len(value):
                raise Exception("value \"%s\" is too long for this field." % value)
            
            # fill space on the right with " "'s
            missing_chars_number = self.field_size - len(value)
            return value + missing_chars_number * " "
        else:
            text = str(value)
            if self.decimal_digits != 0 or type(value) is float:
                number_of_decimal_places = text.find(".") + 1

                comma_shifts = self.decimal_digits - number_of_decimal_places

                # 1.234
                # expect 2 decimal places
                # 2 - 3 = -1
                # Remove one char

                # 1.234
                # expect 4 decimal places
                # 4 - 3 = 1
                # Add one char

                if comma_shifts < 0:
                    text = text[:comma_shifts]
                else:
                    text += "0" * comma_shifts

            text_length = len(text)
            if self.field_size < text_length:
                raise Exception(f"Number {value} is too large for this field.")

            missing_chars_number = self.field_size - text_length
            text = " " * missing_chars_number + text
            return text

    # string will be filled with "0"s
    def number_to_str_with_window_size(self, number, window_size):
        result_str = str(number)
        missing_chars_number = window_size - len(result_str)
        result_str = missing_chars_number * "0" + result_str
        return result_str

    def __repr__(self):
        return "AdisFieldDefinition: item_number=%s, field_size=%d, decimal_digits=%d" \
            % (self.item_number, self.field_size, self.decimal_digits)
