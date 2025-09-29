import requests

from test.config import BASE_URL, headers

def test_get_chapter_content():
    """测试获取章节内容"""
    response = requests.get(f"{BASE_URL}/book/chapter/1", headers=headers)
    assert response.status_code == 200


def test_get_chapter_content_with_params():
    """测试通过参数获取章节内容"""
    book_id = 1
    chapter_index = 1
    response = requests.get(f"{BASE_URL}/book/chapter/{book_id}/{chapter_index}", headers=headers)
    assert response.status_code == 200
def test_get_book_info():
    """测试获取图书信息"""
    book_id = 1
    response = requests.get(f"{BASE_URL}/book/{book_id}", headers=headers)
    print(response.json())
    assert response.status_code == 200

def test_get_book_list():
    """测试获取图书列表"""
    query = ''.join([ f"book_ids={book_id}&" for book_id in [1,2,3]])
    response = requests.get(f"{BASE_URL}/book/list?{query}", headers=headers)
    assert response.status_code == 200

def test_get_book_total():
    """测试获取图书总数"""
    response = requests.get(f"{BASE_URL}/book/total", headers=headers)
    assert response.status_code == 200

