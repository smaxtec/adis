# ADIS-Parser
A Parser for Agricultural Data Interchange Syntax

This parser supports Class A ADIS format.


## Installation


## Quickstart
### Parse an ADIS file and turn it to JSON
```python
# example_adis_to_json.py
from adis_aded_parser import Adis

sample_adis_file = "sample.ads"

adis = Adis.parse_from_file(sample_adis_file)
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
                    "00000000": "Euler number        ",
                    "00000001": 2.718281,
                    "00000002": null
                },
                {
                    "00000000": "Pi                  ",
                    "00000001": 3.141592,
                    "00000002": null
                },
                {
                    "00000000": "Gravity on Earth    ",
                    "00000001": 9.81,
                    "00000002": "ms^(-2)   "
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
                    "00000008": "abc       ",
                    "00000009": "xyz       "
                },
                {
                    "00000008": "def       ",
                    "00000009": "uvw       "
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
                    "00000006": "         1",
                    "00000007": 1.23
                },
                {
                    "00000006": "         2"
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
from adis_aded_parser import Adis

sample_json_file = "sample.json"

adis = Adis.from_json_file(sample_json_file)
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
Each file can contain multiple logical ADIS files.
Each of these logical ADIS files consists of one or multiple blocks.
Each block contains the definitions for the fields and one or multiple
data rows.
