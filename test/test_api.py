import requests
import time

isLocal = False


def upload_test():
    if isLocal:
        url = 'http://localhost:5001/upload/'
    else:
        url = 'http://158.247.236.199:5001/upload/'
        url = "http://203.253.21.171:5001/upload/"
        url = "http://203.253.21.171:5000/upload/"

    file_path = 'test.zip'
    file_path = 'npm-lockfile-38f99c3374ca4e9bd75f3ec34f3edb249eb391cf.zip'

    with open(file_path, 'rb') as f:
        files = {'file': f}
        headers = {
            'accept': 'application/json'
        }

        response = requests.post(url, headers=headers, files=files)

        print(response.status_code)
        if response.status_code == 200:
            print(response.json())
            return response.json()['id']
        else:
            print(response.text)

def file_test(file_id):
    if isLocal:
        url = "http://localhost:5001/files/" + str(file_id)
    else:
        url = "http://158.247.236.199:5001/file/" + str(file_id)
        url = "http://203.253.21.171:5001/file/" + str(file_id)
        url = "http://203.253.21.171:5000/file/" + str(file_id)

    response = requests.get(url)
    print(response.status_code)
    print(response.json())
    return response.json()

def filelist_test():
    if isLocal:
        url = "http://localhost:5001/files/"
    else:
        url = "http://158.247.236.199:5001/files/"
        url = "http://203.253.21.171:5001/files/"
        url = "http://203.253.21.171:5000/files/"

    response = requests.get(url)
    print(response.status_code)
    print(response.json())

def analysis_test(file_id):
    if isLocal:
        url = "http://localhost:5001/analyze/?file_id=1"
    else:
        url = "http://158.247.236.199:5001/analyze/?file_id=1"
        url = f"http://203.253.21.171:5001/analyze/?file_id={file_id}"
        url = f"http://203.253.21.171:5000/analyze/?file_id={file_id}"
    
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.get(url)
    print(response.status_code)
    print(response.json())

def patch_test(file_id):
    if isLocal:
        url = "http://localhost:5001/patch/?file_id=1"
    else:
        url = f"http://203.253.21.171:5001/patch/?file_id={file_id}"
        url = f"http://203.253.21.171:5000/patch/?file_id={file_id}"
    
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(url)
    print(response.status_code)
    print(response.json())

def download_report(file_id):
    if isLocal:
        url = "http://localhost:5001/report/?file_id=1"
    else:
        url = f"http://203.253.21.171:5000/download-report/?file_id={file_id}"
    
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(url)
    print(response.status_code)
    
    with open("patch-" + str(int(time.time())) + ".md", "wb") as f:
        print(f'patch file : patch-{int(time.time())}.md')
        f.write(response.content)


if __name__ == "__main__":
    file_id = upload_test()
    print('-'*50)
    filelist_test()
    print('-'*50)
    analysis_test(file_id)
    print('-'*50)
    patch_test(file_id)
    print('-'*50)
    while True:
        if file_test(file_id)['is_patched']:
            print('-'*50)
            break
        time.sleep(5)
    print('-'*50)
    download_report(file_id)