from .adis_block import AdisBlock
from .adis_lines import DefinitionLine

class AdisFile:
    def __init__(self, blocks):
        self.blocks = blocks

    def get_blocks(self):
        return self.blocks

    @staticmethod
    def from_lines(lines):

        blocks_of_lines = AdisFile.split_lines_into_blocks(lines)
        blocks = []

        for block_of_lines in blocks_of_lines:
            blocks.append(AdisBlock.from_lines(block_of_lines))

        return AdisFile(blocks)

    # Each block starts with a definition
    @staticmethod
    def split_lines_into_blocks(lines):
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
        data = {}
        for block in self.blocks:
            data[block.get_entity_number()] = block.to_dict()
        return data

    def __repr__(self):
        return "AdisFile contains %d blocks" % len(self.blocks)
