from aiogram.filters.callback_data import CallbackData
from uuid import UUID


class PaymentCallback(CallbackData, prefix="payment"):
    user_id: UUID
