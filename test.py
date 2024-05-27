import requests

def upload_test():
    url = "http://localhost:8000/upload/"
    file_path = 'test.zip'

    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, "application/zip")}
        response = requests.post(url, files=files)

    print(response.status_code)
    print(response.json())

def filelist_test():
    url = "http://localhost:8000/files/"

    response = requests.get(url)
    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    filelist_test()