import requests

with open("win.replay", "rb") as f:
    data = bytearray(f.read())

url = "http://localhost:8533"
payload = bytes(data)

response = requests.post(url, data=payload)
print(response.content) # should give the flag
