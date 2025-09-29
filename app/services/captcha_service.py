from string import ascii_letters, digits
from random import choices
from typing import Tuple
from uuid import uuid4
from captcha.image import ImageCaptcha

from app.core import settings
from app.services.cache_service import cache_delete, cache_get, cache_set


class CaptchaService:

    @staticmethod
    def generate_captcha_text(length: int = 4) -> str:
        """
        生成随机验证码
        :param length: 验证码长度
        :return: 验证码
        """
        return ''.join(choices(ascii_letters + digits, k=length))

    @staticmethod
    async def get_captcha(
            length: int = 4,
            width: int = 160,
            height: int = 60,
            expire: int = settings.CAPTCHA_EXPIRE  # 2分钟
    ) -> Tuple[bytes, str]:
        """生成验证码图片并缓存，返回图片 bytes 和 ID"""
        text = CaptchaService.generate_captcha_text(length)
        image = ImageCaptcha(width=width, height=height)
        image_bytes = image.generate(text).getvalue()  # 直接获取 bytes

        captcha_id = str(uuid4())
        await cache_set(
            key_prefix=f"captcha:{captcha_id}",
            value=text,
            expire=expire
        )
        return image_bytes, captcha_id

    @staticmethod
    async def verify_captcha(captcha_id: str, captcha_text: str) -> bool:
        """
        验证验证码
        :param captcha_id: 验证码ID
        :param captcha_text: 验证码文本
        :return: 验证结果
        """
        cached_text = await cache_get(
            key_prefix=f"captcha:{captcha_id}",
        )
        if cached_text is None:
            return False
        if cached_text.lower() == captcha_text.lower():
            await cache_delete(
                key_prefix=f"captcha:{captcha_id}",
            )
            return True
        return False
