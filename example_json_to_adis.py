from adis_parser import Adis

adis = Adis.from_json_file("sample.json")
generated_adis_text = adis.dumps()

print(generated_adis_text)
