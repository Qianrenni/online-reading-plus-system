import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


class EpubParser:
    """
    EPUB文件解析器，使用线程池处理CPU密集型任务
    """
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def _parse_epub_sync(self, file_path: str) -> Dict:
        """
        同步解析EPUB文件
        """
        book = epub.read_epub(file_path)
        chapters = []
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                title = soup.title.string if soup.title else "Unknown Chapter"
                content = soup.get_text()
                chapters.append({
                    "title": title,
                    "content": content
                })
        
        return {
            "title": book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else "Unknown Title",
            "author": book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else "Unknown Author",
            "chapters": chapters
        }
    
    async def parse_epub(self, file_path: str) -> Dict:
        """
        异步解析EPUB文件
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, self._parse_epub_sync, file_path)
        return result
    
    def close(self):
        """
        关闭线程池
        """
        self.executor.shutdown(wait=True)


# 全局EPUB解析器实例
epub_parser = EpubParser()