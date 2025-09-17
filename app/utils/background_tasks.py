import asyncio
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor


class BackgroundTasks:
    """
    后台任务调度器
    """
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = []
    
    async def add_task(self, func: Callable, *args, **kwargs) -> Any:
        """
        添加后台任务
        """
        loop = asyncio.get_event_loop()
        task = loop.run_in_executor(self.executor, func, *args, **kwargs)
        self.tasks.append(task)
        return await task
    
    async def wait_for_tasks(self):
        """
        等待所有任务完成
        """
        if self.tasks:
            await asyncio.gather(*self.tasks)
            self.tasks.clear()
    
    def close(self):
        """
        关闭线程池
        """
        self.executor.shutdown(wait=True)


# 全局后台任务实例
background_tasks = BackgroundTasks()