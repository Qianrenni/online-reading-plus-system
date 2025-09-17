from typing import Dict, Any
from alipay import AliPay
from app.config.settings import settings


class AlipayWrapper:
    """
    支付宝支付封装类
    """
    
    def __init__(self):
        self.alipay = AliPay(
            appid=settings.alipay_app_id,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=settings.alipay_private_key,
            alipay_public_key_string=settings.alipay_public_key,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=False  # 默认False
        )
    
    async def create_payment(self, out_trade_no: str, total_amount: float, subject: str) -> str:
        """
        创建支付订单
        """
        order_string = self.alipay.api_alipay_trade_page_pay(
            out_trade_no=out_trade_no,
            total_amount=total_amount,
            subject=subject,
            return_url="http://localhost:8000/payment/return",
            notify_url="http://localhost:8000/payment/notify"
        )
        return f"https://openapi.alipay.com/gateway.do?{order_string}"
    
    async def verify_payment(self, data: Dict[str, str], signature: str) -> bool:
        """
        验证支付结果
        """
        success = self.alipay.verify(data, signature)
        return success


# 全局支付宝实例
alipay_client = AlipayWrapper()