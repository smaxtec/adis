from adis_aded_parser import Adis

sample_json_file = "sample.json"

adis = Adis.from_json_file(sample_json_file)
generated_adis_text = adis.dumps()

print(generated_adis_text)
