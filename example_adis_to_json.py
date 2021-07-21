from adis_aded_parser import Adis

sample_adis_file = "sample.ads"

adis = Adis.parse_from_file(sample_adis_file)
generated_json = adis.to_json()

print(generated_json)
