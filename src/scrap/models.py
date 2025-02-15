class LotFields:
    """
    Класс, описывающий поля лота со страницы редактирования лота.

    :param lot_id: ID лота.
    :type lot_id: :obj:`int`

    :param fields: словарь с полями.
    :type fields: :obj:`dict`
    """
    def __init__(self, lot_id: int, fields: dict):
        self.lot_id: int = lot_id
        """ID лота."""
        self.__fields: dict = fields
        """Поля лота."""

        self.title_ru: str | None = self.__fields.get("fields[summary][ru]")
        """Русское краткое описание (название) лота."""
        self.title_en: str | None = self.__fields.get("fields[summary][en]")
        """Английское краткое описание (название) лота."""
        self.description_ru: str | None = self.__fields.get("fields[desc][ru]")
        """Русское полное описание лота."""
        self.description_en: str | None = self.__fields.get("fields[desc][en]")
        """Английское полное описание лота."""
        self.amount: int | None = int(i) if (i := self.__fields.get("amount")) else None
        """Кол-во товара."""
        self.price: float | None = float(i) if (i := self.__fields.get("price")) else None
        """Цена за 1шт."""
        self.active: bool = "active" in self.__fields
        """Активен ли лот."""
        self.deactivate_after_sale: bool = "deactivate_after_sale[]" in self.__fields
        """Деактивировать ли лот после продажи."""

    @property
    def fields(self) -> dict[str, str]:
        """
        Возвращает все поля лота в виде словаря.

        :return: все поля лота в виде словаря.
        :rtype: :obj:`dict` {:obj:`str`: :obj:`str`}
        """
        return self.__fields

    def edit_fields(self, fields: dict[str, str]):
        """
        Редактирует переданные поля лота.

        :param fields: поля лота, которые нужно заменить, и их значения.
        :type fields: obj:`dict` {:obj:`str`: :obj:`str`}
        """
        self.__fields.update(fields)

    def set_fields(self, fields: dict):
        """
        Сбрасывает текущие поля лота и устанавливает переданные.
        !НЕ РЕДАКТИРУЕТ СВОЙСТВА ЭКЗЕМЛПЯРА!

        :param fields: поля лота.
        :type fields: :obj:`dict` {:obj:`str`: :obj:`str`}
        """
        self.__fields = fields

    def renew_fields(self) -> "LotFields":
        """
        Обновляет :py:obj:`~__fields` (возвращается в методе :meth:`FunPayAPI.types.LotFields.get_fields`),
        основываясь на свойствах экземпляра.
        Необходимо вызвать перед сохранением лота на FunPay после изменения любого свойства экземпляра.

        :return: экземпляр класса :class:`FunPayAPI.types.LotFields` с новыми полями лота.
        :rtype: :class:`FunPayAPI.types.LotFields`
        """
        self.__fields["fields[summary][ru]"] = self.title_ru
        self.__fields["fields[summary][en]"] = self.title_en
        self.__fields["fields[desc][ru]"] = self.description_ru
        self.__fields["fields[desc][en]"] = self.description_en
        self.__fields["price"] = str(self.price) if self.price is not None else ""
        self.__fields["deactivate_after_sale"] = "on" if self.deactivate_after_sale else ""
        self.__fields["active"] = "on" if self.active else ""
        self.__fields["amount"] = self.amount if self.amount is not None else ""
        return self
    
    def get_products(self):
        secrets: str = self.__fields["secrets"]
        return secrets.split("\n")