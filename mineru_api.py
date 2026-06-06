import requests
import os
import time

token = "personal api"
url = "https://mineru.net/api/v4/file-urls/batch"
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}
data = {
    "files": [
        {"name":"agent_word.pdf", "data_id": "abcd"}
    ],
    "model_version":"vlm"
}
file_path = ["agent_word.pdf"]
try:
    response = requests.post(url,headers=header,json=data)
    if response.status_code == 200:
        result = response.json()
        print('response success. result:{}'.format(result))
        if result["code"] == 0:
            batch_id = result["data"]["batch_id"]
            urls = result["data"]["file_urls"]
            print('batch_id:{},urls:{}'.format(batch_id, urls))
            for i in range(0, len(urls)):
                with open(file_path[i], 'rb') as f:
                    res_upload = requests.put(urls[i], data=f)
                    if res_upload.status_code == 200:
                        print(f"{urls[i]} upload success")
                    else:
                        print(f"{urls[i]} upload failed")
        else:
            print('apply upload url failed,reason:{}'.format(result["msg"]))
    else:
        print('response not success. status:{} ,result:{}'.format(response.status_code, response))
except Exception as err:
    print(err)

time.sleep(20)

batch_id = response.json()['data']['batch_id']
url = f"https://mineru.net/api/v4/extract-results/batch/05621608-2c28-4394-86c9-a5c7b7e697e5"
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

res = requests.get(url, headers=header)
zip_url = res.json()["data"]['extract_result'][0]['full_zip_url']
os.system('wget {0}'.format(zip_url))

zip_file_name = zip_url.split('/')[-1]

os.system('unzip {0} -d {1}'.format(zip_file_name, zip_file_name.split('.')[0]))
