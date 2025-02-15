from aiogram.filters.callback_data import CallbackData


class StaticCallback(CallbackData, prefix="static"):
    static_code: str

class AddStaticCallback(CallbackData, prefix="add_static"):
    pass
