from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles
import os

router = APIRouter(prefix="/static")


# 注意：实际部署时推荐使用Nginx托管静态文件
# 这里仅用于开发环境下的静态文件访问