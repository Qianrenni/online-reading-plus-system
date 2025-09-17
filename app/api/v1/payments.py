from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.payment import PaymentHistory
from app.config.database import get_db

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/history", response_model=List[PaymentHistory])
async def read_payment_history(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    # 获取用户支付历史
    pass


@router.post("/alipay")
async def alipay_payment(
    amount: float,
    db: AsyncSession = Depends(get_db)
):
    # 发起支付宝支付
    pass


@router.post("/recharge")
async def recharge_balance(
    amount: float,
    db: AsyncSession = Depends(get_db)
):
    # 余额充值
    pass