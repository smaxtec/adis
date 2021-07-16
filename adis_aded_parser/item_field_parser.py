STRICT_MODE = False

class ItemFieldParser:
    def __init__(self, item_number, field_size, decimal_digits):
        self.item_number = item_number
        self.field_size = int(field_size)
        self.decimal_digits = int(decimal_digits)
    
    def get_field_size(self):
        return self.field_size

    def parse_at_position(self, raw_text, position):
        # return a string when decimal_digits is 0 / otherwise float
        result = {
            "item_number": self.item_number,
            "value": raw_text[position:position + self.field_size]
        }
        
        value_size = len(result["value"])
        if STRICT_MODE:
            if value_size != self.field_size:
                raise Exception("""Expected field size of %d chars, but got field size of %d chars.
                    Turning strict mode off might fix this problem."""
                    % (self.field_size, value_size))
        else:
            if value_size != 0 and value_size != self.field_size:
                raise Exception("""Expected field size of %d chars or an empty field, but got
                    field size of %d chars.""" % (self.field_size, value_size))
            elif value_size == 0:
                result["value"] = None      # Not sure if that's right - how do we handle undefined vs null values
                return result

        # null value field        
        if self.only_contains_char(result["value"], "?"):
            result["value"] = None
            return result

        # handle case where it's a decimal number
        if self.decimal_digits != 0:
            result["value"] = self.parse_number(result["value"])
            result["value"] /= 10**self.decimal_digits
        return result
    
    def parse_number(self, text):
        return float(text.replace(" ", ""))

    def only_contains_char(self, text, allowed_char):
        for char in text:
            if char != allowed_char:
                return False
        return True

    def __repr__(self):
        return "ItemFieldParser: item_number=%s, field_size=%d, decimal_digits=%d" \
            % (self.item_number, self.field_size, self.decimal_digits)
