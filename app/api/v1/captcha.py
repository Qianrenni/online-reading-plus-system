from fastapi import APIRouter, Response
from starlette import status

from app.core import wrap_error_handler_api
from app.services.captcha_service import CaptchaService

captcha_router = APIRouter(prefix='/captcha', tags=["captcha"])


@captcha_router.get('/get')
@wrap_error_handler_api(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
async def get_captcha():
    """
    获取验证码
    :return: 验证码图片 bytes
    """
    image_bytes, captcha_id = await CaptchaService.get_captcha()

    return Response(
        content=image_bytes,
        media_type="image/png",
        headers={"X-Captcha-ID": captcha_id}
    )
