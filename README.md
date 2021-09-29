# ADIS
A python package for parsing and creating ADIS (Agricultural Data Interchange Syntax) files. 

This parser supports **Class A** ADIS format.

[ADIS Standardization document](https://www.iso.org/obp/ui/#iso:std:iso:11787:ed-1:v1:en)

[Wikipedia artice (unfortunately only available in german)](https://de.wikipedia.org/wiki/Agricultural_Data_Interchange_Syntax)

## Installation
```
pip install adis
```

## Examples
### Parse an ADIS file and turn it to JSON
```python
# example_adis_to_json.py
from adis import Adis

adis = Adis.parse_from_file("sample.ads")
generated_json = adis.to_json()

print(generated_json)
```
Prettyprinted output:
```json
[
    {
        "990001": {
            "definitions": [
                {
                    "item_number": "00000000",
                    "field_size": 20,
                    "decimal_digits": 0
                },
                {
                    "item_number": "00000001",
                    "field_size": 9,
                    "decimal_digits": 6
                },
                {
                    "item_number": "00000002",
                    "field_size": 10,
                    "decimal_digits": 0
                }
            ],
            "data": [
                {
                    "00000000": "Euler number",
                    "00000001": 2.718281,
                    "00000002": null
                },
                {
                    "00000000": "Pi",
                    "00000001": 3.141592,
                    "00000002": null
                },
                {
                    "00000000": "Gravity on Earth",
                    "00000001": 9.81,
                    "00000002": "ms^(-2)"
                }
            ],
            "status": "H"
        },
        "990002": {
            "definitions": [
                {
                    "item_number": "00000008",
                    "field_size": 10,
                    "decimal_digits": 0
                },
                {
                    "item_number": "00000009",
                    "field_size": 10,
                    "decimal_digits": 0
                }
            ],
            "data": [
                {
                    "00000008": "abc",
                    "00000009": "xyz"
                },
                {
                    "00000008": "def",
                    "00000009": "uvw"
                }
            ],
            "status": "N"
        }
    },
    {
        "990001": {
            "definitions": [
                {
                    "item_number": "00000006",
                    "field_size": 10,
                    "decimal_digits": 0
                },
                {
                    "item_number": "00000007",
                    "field_size": 5,
                    "decimal_digits": 2
                }
            ],
            "data": [
                {
                    "00000006": "1",
                    "00000007": 1.23
                },
                {
                    "00000006": "2"
                }
            ],
            "status": "H"
        }
    }
]
```


### Turn a JSON file to ADIS
```python
# example_json_to_adis.py
from adis import Adis

adis = Adis.from_json_file("sample.json")
generated_adis_text = adis.dumps()

print(generated_adis_text)
```
Output:
```
DH990001000000002000000000109600000002100
VH990001Euler number          2718281??????????
VH990001Pi                    3141592??????????
VH990001Gravity on Earth      9810000ms^(-2)   
DN9900020000000810000000009100
VN990002abc       xyz       
VN990002def       uvw       
EN
DH9900010000000610000000007052
VH990001         1  123
VH990001         2|||||
ZN

```

## About the ADIS format
Each physical file can contain multiple logical ADIS files, these are represented by objects of the type `AdisFile`.
Each of those logical ADIS files contains one or multiple blocks, these are represented by objects of the type `AdisBlock`.
Each block consists of the definitions for the fields (list of objects of type `AdisFieldDefinition`) and one or multiple
data rows (list of list of `AdisValue`).

## Documentation
This documentation only contains methods that are inteded to be used by the user.
Take a look at the docstrings for more information about methods.

### Adis
Static methods:
* `parse(text)`: Creates an `Adis` object from a text that's in the ADIS format
* `parse_from_file(path_to_file)`: Creates an `Adis` object from an ADIS file
* `from_json(json_text)`: Create an `Adis` object from a json text
* `from_json_file(path_to_json_file)`: Create an `Adis` object from a json file

Normal methods:
* `__init__(adis_files)`: Creates an `Adis` object from a list of `AdisFile`s
* `to_json(strip_string_values=True)`: Creates a json text containing the files, definitions and data
* `dumps()`: Creates a text in the ADIS format
* `get_files()`: Returns a list of `AdisFile`s

### AdisFile
Normal methods:
* `__init__(blocks)`: Creates an `AdisFile` from a list of `AdisBlock`s
* `get_blocks()`: Returns a list of `AdisBlock`s

### AdisBlock
Normal methods:
* `__init__(entity_number, status, field_definitions, data_rows)`: Creates an `AdisBlock`
* `get_entity_number()`: Returns the entity number of this `AdisBlock`
* `get_field_definitions()`: Returns the field definitions as list of `AdisFieldDefinition`s
* `get_data_rows()`: Returns the data rows as list. Each data row is a list of `AdisValue`s

### AdisFieldDefinition
Normal methods:
* `__init__(item_number, field_size, decimal_digits)`: Creates an `AdisFieldDefinition`
* `get_item_number()`: Returns the item number
* `get_field_size()`: Returns the field size
* `get_decimal_digits()`: Returns the number of decimal digits

### AdisValue
Static flags:
* `strip_string_values`: String values that are returned by `to_dict()` will be
    stripped if this flag is set.

Normal methods:
* `__init__(item_number, value)`: Creates an `AdisValue`
* `to_dict()`: Returns a dict containing the item number and value of this `AdisValue`
