from sqlmodel import select,insert

from app.core.database import DataBaseSessionDepency
from app.models.sql import Shelf


class ShelfService:

    @staticmethod
    async  def get_shelf(
            user_id: int,
            database: DataBaseSessionDepency
    ):
        """
        获取用户书架
        :param user_id: 用户ID
        :param database:      数据库会话
        :return:     书架列表
        """
        statement = select(Shelf.book_id, Shelf.last_read_at).where(Shelf.user_id == user_id)
        result = await database.exec(statement)
        return  result.all()


    @staticmethod
    async def add_shelf(
            book_id: int,
            user_id: int,
            database: DataBaseSessionDepency
    ):
        """
        添加图书到书架
        :param book_id:  图书ID
        :param user_id:    用户ID
        :param database:      数据库会话
        :return:          添加结果
        """
        try:
            item = Shelf(book_id=book_id, user_id=user_id)
            database.add(item)
            await database.commit()
            return True
        except Exception as e:
            raise  Exception("添加失败",e)
shelf_service = ShelfService()