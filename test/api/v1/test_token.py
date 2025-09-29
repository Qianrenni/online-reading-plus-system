from test.config import BASE_URL, headers, REFRESH_TOKEN
import requests


def test_get_token():
    url = BASE_URL + '/token/get'
    body = {
        "username": "3092176591@qq.com",
        "password": "123456"
    }
    response = requests.post(url=url, data=body)
    print(response.text)

def  test_refresh_token():
    url = BASE_URL + '/token/refresh'
    headers = {
        'Authorization': f'Bearer {REFRESH_TOKEN}'
    }
    response = requests.post(url=url, headers=headers)
    print(response.text)