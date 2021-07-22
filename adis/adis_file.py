from .adis_block import AdisBlock
from .adis_lines import DefinitionLine

"""
An AdisFile contains multiple AdisBlocks.
"""

class AdisFile:
    def __init__(self, blocks):
        """Creates a new AdisFile

        Args:
            blocks (list[AdisBlock]): blocks that are located in this file
        """
        self.blocks = blocks

    def get_blocks(self):
        """Returns a list of AdisBlocks that are in this AdisFile

        Returns:
            list[AdisBlock]: AdisBlocks in this AdisFile
        """
        return self.blocks

    @staticmethod
    def from_lines(lines):
        """Creates a new AdisFile from the provided lines.

        Args:
            lines (list[AdisLine]): the AdisFile will be created on base of these lines

        Returns:
            AdisFile: the new AdisFile
        """
        blocks_of_lines = AdisFile.split_lines_into_blocks(lines)
        blocks = []

        for block_of_lines in blocks_of_lines:
            blocks.append(AdisBlock.from_lines(block_of_lines))

        return AdisFile(blocks)

    @staticmethod
    def from_dict(file_dict):
        """Creates a new AdisFile from the provided dict.

        Args:
            file_dict (dict): contains information about the contents of this file

        Returns:
            AdisFile: the new AdisFile
        """
        blocks = []
        for entity_number in file_dict:
            block_dict = file_dict[entity_number]
            adis_block = AdisBlock.from_dict(entity_number, block_dict)
            blocks.append(adis_block)
        return AdisFile(blocks)

    # Each block starts with a definition
    @staticmethod
    def split_lines_into_blocks(lines):
        """Splits the lines into blocks of lines.

        Args:
            lines (list[AdisLine]): list of AdisLines of this file

        Returns:
            list[list[AdisLine]]: list that contains a list of lines for each block in this \
                AdisFile
        """
        blocks = []
        current_block = []

        for line in lines:
            if type(line) == DefinitionLine:
                # start of a new block
                if len(current_block) != 0:
                    blocks.append(current_block)
                current_block = [line]
            else:
                current_block.append(line)
        
        if len(current_block) != 0:
            blocks.append(current_block)

        return blocks

    def to_dict(self):
        """Creates a dict from the AdisFile.

        Returns:
            dict: contains all data of the blocks in this file
        """
        data = {}
        for block in self.blocks:
            data[block.get_entity_number()] = block.to_dict()
        return data

    def dumps(self):
        """Creates an ADIS text from this AdisFile.

        Returns:
            string: ADIS text of this AdisFile
        """
        text = ""
        for block in self.blocks:
            text += block.dumps()

        return text

    def __repr__(self):
        return "AdisFile contains %d blocks" % len(self.blocks)
