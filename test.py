import requests

BASE = "http://127.0.0.1:5000/"

#response = requests.patch(BASE + "video/1",{"name":"MAJAJA"})
response = requests.delete(BASE + "video/1")
response = requests.get(BASE + "video/1")
print(response.json())

