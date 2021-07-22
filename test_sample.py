from adis import (
    Adis,
    AdisBlock,
    AdisFieldDefinition
)
from adis.adis_lines import (
    AdisLine,
    CommentLine,
    DefinitionLine,
    ValueLine
)

import pytest
import os
import json

directory = os.path.dirname(__file__)
if directory == "":
    directory = os.getcwd()


demo_json_file = os.path.join(directory, "sample.json")
demo_adis_file = os.path.join(directory, "sample.ads")
with open(demo_json_file, "r") as input_file:
    json_input_data = json.loads(input_file.read())

adis = Adis.from_json_file(demo_json_file)
generated_json = adis.to_json()
json_output_data = json.loads(generated_json)

adis_out = adis.dumps()

adis2 = Adis.parse(adis_out)
adis2_out = adis2.dumps()


def test_json_input_and_output():
    assert json_input_data == json_output_data

def test_adis_input_and_output():
    assert adis_out == adis2_out

def test_get_files():
    adis_files = adis.get_files()
    assert len(adis_files) == 2

def test_parse_adis_file():
    adis_from_adis_file = Adis.parse_from_file(demo_adis_file)
    adis_from_json_file = Adis.from_json_file(demo_json_file)
    assert adis_from_adis_file.dumps() == adis_from_json_file.dumps()

def test_repr():
    assert adis.__repr__() == "Adis containing 2 Adis-files"

    adis_file = adis.get_files()[0]
    assert adis_file.__repr__() == "AdisFile contains 2 blocks"

    adis_block = adis_file.get_blocks()[0]
    assert adis_block.__repr__() == "AdisBlock with status=H and entity_number=990001 " \
        "containing 3 data row(s)"

    adis_value = adis_block.get_data_rows()[0][0]
    assert adis_value.__repr__() == "AdisValue: item_number=00000000, value=Euler number"

    adis_field_definition = AdisFieldDefinition("12345678", 1, 1)
    assert adis_field_definition.__repr__() == "AdisFieldDefinition: item_number=12345678, " \
        "field_size=1, decimal_digits=1"
    
    adis_line = AdisLine.parse_line("EN")
    assert adis_line.__repr__() == "End of logical file status: normal, line: EN"

def test_from_json_exceptions():
    with pytest.raises(Exception, match="The root element of the JSON has to be a list. " \
        "Got <class 'dict'>."):
        adis_from_json = Adis.from_json("{}")

    with pytest.raises(Exception, match="Expecting a dict but got <class 'list'>."):
        adis_from_json = Adis.from_json("[{}, []]")

def test_adis_block_getters():
    adis_block = adis.get_files()[0].get_blocks()[0]
    assert len(adis_block.get_field_definitions()) == 3
    assert len(adis_block.get_data_rows()) == 3

def test_adis_block_exceptions():
    with pytest.raises(Exception,
        match="The entity number has to be a string consisting of 6 chars."):
        AdisBlock("123", "N", [], [])

    with pytest.raises(Exception,
        match="Invalid status char. Has to be one of "):
        AdisBlock("123456", "A", [], [])

    with pytest.raises(Exception,
        match="Status may only be one char."):
        AdisBlock("123456", "NN", [], [])
    
    with pytest.raises(Exception,
        match="\"status\" field is missing in block dict."):
        AdisBlock.from_dict("123456", {})
    
    with pytest.raises(Exception,
        match="\"definitions\" field is missing in block dict."):
        AdisBlock.from_dict("123456", {
            "status": "N"
        })

    with pytest.raises(Exception,
        match="\"data\" field is missing in block dict."):
        AdisBlock.from_dict("123456", {
            "status": "N",
            "definitions": []
        })

    with pytest.raises(Exception,
        match="A field definition has to be a dict but got <class 'list'>."):
        AdisBlock.from_dict("123456", {
            "status": "N",
            "definitions": [[]],
            "data": []
        })

    with pytest.raises(Exception,
        match="The data of each block has to be a list. Got <class 'dict'>."):
        AdisBlock.from_dict("123456", {
            "status": "N",
            "definitions": [],
            "data": {}
        })

    with pytest.raises(Exception,
        match="Each data row has to be a dict. Got <class 'float'>."):
        AdisBlock.from_dict("123456", {
            "status": "N",
            "definitions": [],
            "data": [3.14]
        })
    
    with pytest.raises(Exception,
        match="Definition line is missing before value line"):
        lines = []
        lines.append(AdisLine.parse_line("VN123456helloworld"))
        AdisBlock.from_lines(lines)

    with pytest.raises(Exception,
        match="Definition is missing."):
        AdisBlock.from_lines([])

def test_adis_line():
    with pytest.raises(Exception,
        match="Linetype End of logical file may not have status faulty"):
        AdisLine.parse_line("EF")
    
    line = AdisLine.parse_line("VN123456abcdef")
    assert line.get_type_char() == "V"
    assert line.get_entity_number() == "123456"

    with pytest.raises(Exception,
        match="Length of definitions text is 10 but it has to be a multiple of 11"):
        AdisLine.parse_line("DN1234561234567890")

    line = AdisLine.parse_line("VN123456abc")
    definitions = []
    definition_for_5_chars = AdisFieldDefinition("12345678", 5, 0)
    definitions.append(definition_for_5_chars)
    definitions.append(definition_for_5_chars)
    with pytest.raises(Exception,
        match="Expecting an item text length of 10 chars or 5 chars, but got 3 chars."):
        line.parse(definitions)

def test_comment_line():
    line = AdisLine.parse_line("CNHello World")
    assert type(line) == CommentLine
    assert line.get_comment() == "Hello World"

def test_adis_field_definition():
    with pytest.raises(Exception,
        match="The item_number has to be a string with length = 8. Got \"1234567\""):
        AdisFieldDefinition("1234567", None, None)
    
    with pytest.raises(Exception,
        match="The field size has to be a number between 1 and 99. Got 0."):
        AdisFieldDefinition("12345678", 0, None)
    
    with pytest.raises(Exception,
        match="The field size has to be a number between 1 and 99. Got 100."):
        AdisFieldDefinition("12345678", 100, None)
    
    with pytest.raises(Exception,
        match="The number of decimal digits has to be a number between 0 and 9. Got -1."):
        AdisFieldDefinition("12345678", 1, -1)
    
    with pytest.raises(Exception,
        match="The number of decimal digits has to be a number between 0 and 9. Got 10."):
        AdisFieldDefinition("12345678", 1, 10)
    
    adis_field_definition = AdisFieldDefinition("12345678", 1, 1)
    assert adis_field_definition.get_item_number() == "12345678"
    assert adis_field_definition.get_field_size() == 1
    assert adis_field_definition.get_decimal_digits() == 1

    with pytest.raises(Exception,
        match="Number 0.1 is too large for this field."):
        adis_field_definition.dumps_value(0.1)
    
    adis_field_definition = AdisFieldDefinition("12345678", 5, 0)
    with pytest.raises(Exception,
        match="value \"123456\" is too long for this field."):
        adis_field_definition.dumps_value("123456")

    with pytest.raises(Exception,
        match="Expected field size of 5 chars or an empty field, but got " \
                "field size of 4 chars."):
        adis_field_definition.parse_field_at_position("1234", 0)
    
    assert adis_field_definition.parse_field_at_position("123", 3).value is None
