from adis import Adis

adis = Adis.parse_from_file("sample.ads")
generated_json = adis.to_json()

print(generated_json)
