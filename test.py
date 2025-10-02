import pymysql
from pymongo import MongoClient
from pymysql import Error

# === MongoDB 连接配置 ===
MONGO_URI = "mongodb://1.95.141.194:27017/"
MONGO_DB = "reading"
MONGO_COLLECTION = "books"


def migrate_data():
    # 连接 MongoDB
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client[MONGO_DB]
    mongo_collection = mongo_db[MONGO_COLLECTION]

    try:

        # 查询 MongoDB 文档（这里查所有，你可加 filter）
        for doc in mongo_collection.find():
            # 提取字段，处理嵌套结构
            print(doc.get("book_id"))

        #     # 插入 MySQL
        #     insert_query = """
        #         INSERT INTO users (name, email, age, city, street)
        #         VALUES (%s, %s, %s, %s, %s)
        #     """
        #     cursor.execute(insert_query, (name, email, age, city, street))
        #
        # # 提交事务
        # mysql_conn.commit()
        print("数据迁移完成！")

    except Error as e:
        print(f"MySQL 错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        if mysql_conn and mysql_conn.is_connected():
            cursor.close()
            mysql_conn.close()
        mongo_client.close()

if __name__ == "__main__":
    migrate_data()