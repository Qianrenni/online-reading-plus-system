import requests

from test.config import BASE_URL, headers

def test_add_user_reading_progress():
    """测试添加用户阅读进度"""
    data = {
        "book_id": 1,
        "last_chapter_id": 1,
        "last_position": 1
    }
    response = requests.patch(f"{BASE_URL}/user_reading_progress/add", headers=headers, json=data)
    assert response.status_code == 200

def test_delete_user_reading_progress():
    """测试删除用户阅读进度"""
    book_id = 1
    response = requests.delete(f"{BASE_URL}/user_reading_progress/delete/{book_id}", headers=headers)
    assert response.status_code == 200



def test_user_reading_progress():
    """测试获取用户阅读进度"""
    response = requests.get(f"{BASE_URL}/user_reading_progress/get", headers=headers)
    assert response.status_code == 200
