import time

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from starlette.middleware.cors import CORSMiddleware

from app.api.v1 import user_router
from app.api.v1.book import book_router
from app.api.v1.token import token_router
from app.core.database import create_database_and_tables
from app.middleware.logging import logger
# 在 main.py 中注册
app = FastAPI(docs_url=None)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="./app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r'$http://localhost\.*^',
)


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


app.include_router(token_router)
app.include_router(user_router)

app.include_router(book_router)
