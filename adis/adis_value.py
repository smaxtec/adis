class AdisValue:
    def __init__(self, item_number, value):
        """Creates a AdisValue from the item number and a value of a field.

        Args:
            item_number (string): item number of the field
            value (None, string, int, float): value of the field
        """
        self.item_number = item_number
        self.value = value

    def to_dict(self):
        """Returns the AdisValue as a dict.

        Returns:
            dict: contains item_number and value
        """
        return {
            "item_number": self.item_number,
            "value": self.value
        }

    def __repr__(self):
        return "AdisValue: item_number=%s, value=%s" % (self.item_number, str(self.value))
