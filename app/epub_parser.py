import os

import re

import pymysql
from ebooklib import epub
from bs4 import BeautifulSoup
import ebooklib
import tkinter as tk
from tkinter import filedialog

# === MySQL 连接配置 ===
MYSQL_CONFIG = {
    'host': '1.95.141.194',
    'database': 'reading_plus',
    'user': 'root',
    'password': '123456',
    'charset': 'utf8mb4'
}
mysql_conn = pymysql.connect(**MYSQL_CONFIG)
cursor = mysql_conn.cursor()
UPLOAD_FOLDER = 'static/book'  # 替换为你想存储书籍的文件夹路径

def get_book_id(name):
    try:
        cursor.execute(f"select book.id from book where book.name = '{name}'")
        book_id = cursor.fetchone()[0]
        return book_id
    except Exception as e:
        # print(f"Error getting book id: {e}")
        return None
# 批量处理文件夹中的所有 .epub 文件
def batch_upload_books(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            try:
                if file.lower().endswith('.epub'):
                    epub_path = os.path.join(root, file)
                    print(f"Processing: {epub_path}")

                    # 提取元数据
                    metadata = extract_epub_metadata(epub_path)
                    if not metadata:
                        print(f"Failed to extract metadata for: {epub_path}")
                        continue
                    # 创建唯一目录存储书籍文件

                    # os.makedirs(book_folder, exist_ok=True)

                    # 检查是否为epub文件并提取封面和总页数
                    book_id = get_book_id(metadata['title'])
                    # if book_id:
                    book_folder = os.path.join(UPLOAD_FOLDER, str(book_id))
                    # os.makedirs(book_folder, exist_ok=True)
                    book = epub.read_epub(epub_path)
                    for item in book.get_items():
                        if item.get_type() != ebooklib.ITEM_DOCUMENT and item.get_type() != ebooklib.ITEM_COVER and item.get_type() != ebooklib.ITEM_NAVIGATION:
                            pass
                            # with open(os.path.join(book_folder, re.split(r'[/\\]', item.file_name)[-1]), 'wb') as f:
                            #     f.write(item.content)
                    cover = next(book.get_items_of_type(ebooklib.ITEM_COVER))
                    cover_path = os.path.join(book_folder, re.split(r'[/\\]', cover.file_name)[-1])
                    if cover and cover_path:
                        cover_path = cover_path.replace('\\', '/')
                        # with open(cover_path, 'wb') as f:
                        #     f.write(cover.content)
                    catalog = []
                    for item in book.toc:
                        catalog.append([str(item.title).replace('.', '_'),book.get_item_with_href(
                            item.href).content.decode('utf-8')])
                    # 创建并保存新的书籍对象

                    init_order = 1.0
                    for title, content in catalog:
                        # 确保 content 不超过数据库限制
                        cursor.execute(f"insert into book_chapter(book_id,sort_order,title,content,created_at) values (%s,%s,%s,%s,now())", (book_id, init_order, title, content))
                        init_order += 10
                    cursor.connection.commit()


                    # print(f"New book created: {new_book.name}  {new_book.author} {new_book.category} {new_book.total_chapter} {new_book.cover}  {new_book.description}")
                else:
                    continue
            except Exception as e:
                print(f"Error processing {file}: {str(e)}")
                continue


def extract_epub_metadata(epub_path):
    try:
        book = epub.read_epub(epub_path)
    except Exception as e:
        print(f"Error reading EPUB file: {e}")
        return None
    # 提取元数据
    title = book.get_metadata('DC', 'title')
    authors = book.get_metadata('DC', 'creator')
    description = book.get_metadata('DC', 'description')
    intro_text = None
    if not description:
        item = next(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        if item:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            paragraphs = soup.find_all('p')
            if paragraphs:
                intro_text = ' '.join(p.get_text().strip() for p in paragraphs[:3])  # 取前 3 段
    # 如果没有描述且也没有提取到简介，则生成默认简介
    if not description and not intro_text:
        intro_text = f"{title[0][0] if title else '未知标题'} 是一本由 {'、'.join([author[0] for author in authors]) if authors else '未知作者'} 创作的书籍。"
    return {
        'title': title[0][0] if title else "未知标题",
        'authors': [author[0] for author in authors] if authors else ["未知作者"],
        'description': description[0][0] if description else intro_text,
    }


def run():
    # 使用 tkinter 选择文件夹
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 让用户选择文件夹
    folder_path = filedialog.askdirectory(title="请选择要处理的文件夹")

    if folder_path:

        batch_upload_books(folder_path)
    else:
        print("未选择文件夹，程序退出。")


if __name__ == "__main__":
    run()
