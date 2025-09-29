import requests

from test.config import BASE_URL, headers


def test_get_user_shelf():
    """测试获取用户书架"""
    response = requests.get(f"{BASE_URL}/shelf/get", headers=headers)
    assert response.status_code == 200


def test_add_book_to_shelf():
    """测试添加书籍到书架"""
    data = {"book_id": 1}
    response = requests.post(f"{BASE_URL}/shelf/add", headers=headers, json=data)
    assert response.status_code == 201


def test_delete_book_from_shelf():
    """测试删除书架书籍"""
    response = requests.delete(f"{BASE_URL}/shelf/delete/1", headers=headers)
    assert response.status_code == 200


