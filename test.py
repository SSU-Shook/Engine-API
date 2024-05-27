import requests

url = "http://localhost:8000/upload/"
file_path = 'test.zip'

with open(file_path, "rb") as f:
    files = {"file": (file_path, f, "application/zip")}
    response = requests.post(url, files=files)

print(response.status_code)
print(response.json())