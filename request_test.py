import requests

url = "http://localhost:8000/upload"
text_data = {"prompt": "What is the most played sport?"}
file = open("input/test.csv", "rb")
files = [("files", file)]

response = requests.post(url, data=text_data, files=files)

file.close()

print(response.json())
