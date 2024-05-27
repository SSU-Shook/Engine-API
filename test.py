import requests

def upload_test():
    # url = "http://158.247.236.199:5000/upload/"
    # file_path = 'test.zip'

    # with open(file_path, "rb") as f:
    #     files = {"file": (file_path, f, "application/zip")}

    #     response = requests.post(url, files=files)

    # print(response.status_code)
    # print(response.json())

    url = 'http://158.247.236.199:5000/upload/'
    file_path = 'test.zip'

    with open(file_path, 'rb') as f:
        files = {'file': f}
        headers = {
            'accept': 'application/json'
        }

        response = requests.post(url, headers=headers, files=files)

        print(response.status_code)
        if response.status_code == 200:
            print(response.json())
        else:
            print(response.text)

def filelist_test():
    url = "http://158.247.236.199:5000/files/"

    response = requests.get(url)
    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    filelist_test()
    # upload_test()