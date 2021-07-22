from .adis_value import AdisValue

"""
The AdisFieldDefinition holds information about the size and the decimal places of the data fields.
"""
class AdisFieldDefinition:
    def __init__(self, item_number, field_size, decimal_digits):
        """Creates an AdisFieldDefinition.

        Args:
            item_number (string): item number of the fields
            field_size (string, int): field size in chars
            decimal_digits (string, int): number of decimal places (0 when the field does not \
                hold a text or the number has no decimal places)
        """
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
            raise Exception("The number of decimal digits has to be a number between 0 and 9. " \
                "Got %d." % self.decimal_digits)

    def get_item_number(self):
        """Returns the item number.

        Returns:
            string: item number
        """
        return self.item_number

    def get_field_size(self):
        """Returns the field size.

        Returns:
            int: field size
        """
        return self.field_size

    def get_decimal_digits(self):
        """Returns the number of decimal digits.

        Returns:
            int: number of decimal digits
        """
        return self.decimal_digits

    def parse_field_at_position(self, raw_text, position):
        """Parses 

        Args:
            raw_text (string): raw ADIS file line
            position (int): position where to start to parse the field from

        Returns:
            AdisValue: AdisValue of the parsed field, or None if the value of the field is \
                undefined
        """
        # return a string when decimal_digits is 0 / otherwise float
        item_number = self.item_number
        value = raw_text[position:position + self.field_size]

        value_size = len(value)
        if value_size != 0 and value_size != self.field_size:
            raise Exception("Expected field size of %d chars or an empty field, but got " \
                "field size of %d chars." % (self.field_size, value_size))
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
        """Checks if the provided text only contains the provided char.

        Args:
            text (string): text to check
            allowed_char (string): char that may be in the text

        Returns:
            boolean: True if the text only contains the given char, otherwise False
        """
        for char in text:
            if char != allowed_char:
                return False
        return True

    def to_dict(self):
        """Creates a dict that contains all information from this definition.

        Returns:
            dict: contains the item_number, field_size and decimal_digits
        """
        return {
            "item_number": self.item_number,
            "field_size": self.field_size,
            "decimal_digits": self.decimal_digits
        }

    def dumps(self):
        """Creates a string from this definition that can directly be a part of the defintion \
            line in an ADIS file

        Returns:
            string: definition text
        """
        text = self.item_number
        text += self.number_to_str_with_window_size(self.field_size, 2)
        text += str(self.decimal_digits)    # only 1 char window
        return text

    def dumps_value(self, value, undefined=False):
        """Dumps the provided AdisValue to a string.

        Args:
            value (AdisValue): value that should be turned to a string
            undefined (bool, optional): Whether the value is undefined or not. Defaults to False.

        Returns:
            string: string that holds the given AdisValue in the correct way
        """
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
                decimal_dot_position = text.find(".") + 1
                decimal_dot_position_from_behind = len(text) - decimal_dot_position
                text = text.replace(".", "")
                
                expected_decimal_dot_position_from_behind = self.decimal_digits

                if expected_decimal_dot_position_from_behind > decimal_dot_position_from_behind:
                    decimal_places_to_add = expected_decimal_dot_position_from_behind \
                                                - decimal_dot_position_from_behind
                    text += decimal_places_to_add * "0"
                elif expected_decimal_dot_position_from_behind < decimal_dot_position_from_behind:
                    decimal_places_to_remove = decimal_dot_position_from_behind \
                                                - expected_decimal_dot_position_from_behind
                    text = text[:len(text) - decimal_places_to_remove]

            text_length = len(text)
            if self.field_size < text_length:
                raise Exception(f"Number {value} is too large for this field.")

            missing_chars_number = self.field_size - text_length
            text = " " * missing_chars_number + text
            return text

    def number_to_str_with_window_size(self, number, window_size):
        """Creates a string with a specific length from a number. All chars that are not used get \
            filled up with "0"s

        Args:
            number (int): number that should be turned to string
            window_size (int): how long the string should be

        Returns:
            string: text with specified length that contains the number
        """
        result_str = str(number)
        missing_chars_number = window_size - len(result_str)
        result_str = missing_chars_number * "0" + result_str
        return result_str

    @staticmethod
    def from_dict(definition_dict):
        """Creates an AdisFieldDefinition from a dict.

        Args:
            definition_dict (dict): dict containing the item number, the field size and the \
                decimal digits of field

        Returns:
            AdisFieldDefinition: new AdisFieldDefinition
        """
        item_number = definition_dict["item_number"]
        field_size = definition_dict["field_size"]
        decimal_digits = definition_dict["decimal_digits"]
        return AdisFieldDefinition(item_number, field_size, decimal_digits)

    def __repr__(self):
        return "AdisFieldDefinition: item_number=%s, field_size=%d, decimal_digits=%d" \
            % (self.item_number, self.field_size, self.decimal_digits)
