class AdisValue:
    def __init__(self, item_number, value):
        self.item_number = item_number
        self.value = value

    def to_dict(self):
        return {
            "item_number": self.item_number,
            "value": self.value
        }

    def __repr__(self):
        return "AdisValue: item_number=%s, value=%s" % (self.item_number, str(self.value))
