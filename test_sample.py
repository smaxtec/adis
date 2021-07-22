from adis import Adis
import os
import json

directory = os.path.dirname(__file__)
if directory == "":
    directory = os.getcwd()


demo_json_file = os.path.join(directory, "sample.json")
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
