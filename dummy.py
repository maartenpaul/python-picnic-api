from python_picnic_api.client import PicnicAPI
picnic = PicnicAPI(username='fam.paul@outlook.com', password='Nan0f00d!', country_code="NL")
results = picnic.search("melk")
print(results)