import time

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from starlette.middleware.cors import CORSMiddleware

from app.api import token_router, user_router, book_router, shelf_router, user_reading_progress_router, captcha_router
from app.middleware import RateLimitMiddleware
from app.middleware.logging import logger

# 在 main.py 中注册
app = FastAPI(docs_url=None)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="./app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    RateLimitMiddleware,
    calls=15,
    period=60,
    exclude_paths={"/docs", "/openapi.json", "/health"}  # 排除 Swagger 等
)
# allow_origin_regex=r'$http://localhost\.*^',


@app.middleware('http')
async def log_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.client.host} {request.method} {request.url} {response.status_code} {process_time:.4f}s")
    return response


# 中间件
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",  # ← 国内能访问
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",  # ← 国内能访问
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/")
async def root():
    return {"message": "Hello World"}
#  获取 token  路由
app.include_router(token_router)
# 用户相关
app.include_router(user_router)
# 书籍相关
app.include_router(book_router)
# 书架相关
app.include_router(shelf_router)
# 阅读历史相关
app.include_router(user_reading_progress_router)
#  验证码相关
app.include_router(captcha_router)