import requests

isLocal = True

def upload_test():
    if isLocal:
        url = 'http://localhost:5001/upload/'
    else:
        url = 'http://158.247.236.199:5001/upload/'
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
    if isLocal:
        url = "http://localhost:5001/files/"
    else:
        url = "http://158.247.236.199:5001/files/"

    response = requests.get(url)
    print(response.status_code)
    print(response.json())

def analysis_test():
    if isLocal:
        url = "http://localhost:5001/analyze/"
    else:
        url = "http://158.247.236.199:5001/analyze/"
    
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json={"file_id": 1}, headers=headers)
    print(response.status_code)
    print(response.json())
    
if __name__ == "__main__":
    upload_test()
    filelist_test()
    analysis_test()