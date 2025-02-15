from typing import Any, Literal, Optional
import time
from .models import LotFields
from .exceptions import AccountNotInitiatedError, RequestFailedError, UnauthorizedError
import requests
import json
from bs4 import BeautifulSoup

class Account:
    """
    Класс для управления аккаунтом FunPay.

    :param golden_key: токен (golden_key) аккаунта.
    :type golden_key: :obj:`str`

    :param user_agent: user-agent браузера, с которого был произведен вход в аккаунт.
    :type user_agent: :obj:`str`

    :param requests_timeout: тайм-аут ожидания ответа на запросы.
    :type requests_timeout: :obj:`int` or :obj:`float`

    :param proxy: прокси для запросов.
    :type proxy: :obj:`dict` {:obj:`str`: :obj:`str` or :obj:`None`
    """

    def __init__(self, golden_key: str, user_agent: str | None = None,
                 requests_timeout: int | float = 10, proxy: Optional[dict] = None):
        self.golden_key: str = golden_key
        """Токен (golden_key) аккаунта."""
        self.user_agent: str | None = user_agent
        """User-agent браузера, с которого был произведен вход в аккаунт."""
        self.requests_timeout: int | float = requests_timeout
        """Тайм-аут ожидания ответа на запросы."""
        self.proxy = proxy

        self.html: str | None = None
        """HTML основной страницы FunPay."""
        self.app_data: dict | None = None
        """Appdata."""
        self.id: int | None = None
        """ID аккаунта."""
        self.username: str | None = None
        """Никнейм аккаунта."""

        self.csrf_token: str | None = None
        """CSRF токен."""
        self.phpsessid: str | None = None
        """PHPSESSID сессии."""

        self.__initiated: bool = False

    def method(self, request_method: Literal["post", "get"], api_method: str, headers: dict, payload: Any,
               exclude_phpsessid: bool = False, raise_not_200: bool = False) -> requests.Response:
        """
        Отправляет запрос к FunPay. Добавляет в заголовки запроса user_agent и куки.

        :param request_method: метод запроса ("get" / "post").
        :type request_method: :obj:`str` `post` or `get`

        :param api_method: метод API / полная ссылка.
        :type api_method: :obj:`str`

        :param headers: заголовки запроса.
        :type headers: :obj:`dict`

        :param payload: полезная нагрузка.
        :type payload: :obj:`dict`

        :param exclude_phpsessid: исключить ли PHPSESSID из добавляемых куки?
        :type exclude_phpsessid: :obj:`bool`

        :param raise_not_200: возбуждать ли исключение, если статус код ответа != 200?
        :type raise_not_200: :obj:`bool`

        :return: объект ответа.
        :rtype: :class:`requests.Response`
        """
        headers["cookie"] = f"golden_key={self.golden_key}"
        headers["cookie"] += f"; PHPSESSID={self.phpsessid}" if self.phpsessid and not exclude_phpsessid else ""
        if self.user_agent:
            headers["user-agent"] = self.user_agent
        link = api_method if api_method.startswith(
            "https://funpay.com") else "https://funpay.com/" + api_method
        response = requests.request(
            request_method,
            link,
            headers=headers,
            data=payload,
            timeout=self.requests_timeout,
            proxies=self.proxy or {})
        if response.status_code == 403:
            raise UnauthorizedError(response)
        elif response.status_code != 200 and raise_not_200:
            raise RequestFailedError(response)
        return response

    def get(self, update_phpsessid: bool = False) -> "Account":
        """
        Получает / обновляет данные об аккаунте. Необходимо вызывать каждые 40-60 минут, дабы обновить
        :py:obj:`.Account.phpsessid`.

        :param update_phpsessid: обновить :py:obj:`.Account.phpsessid` или использовать старый.
        :type update_phpsessid: :obj:`bool`, опционально

        :return: объект аккаунта с обновленными данными.
        :rtype: :class:`FunPayAPI.account.Account`
        """
        response = self.method("get",
                               "https://funpay.com",
                               {},
                               {},
                               update_phpsessid,
                               raise_not_200=True)

        html_response = response.content.decode()
        parser = BeautifulSoup(html_response, "html.parser")

        username = parser.find("div", {"class": "user-link-name"})
        if not username:
            raise UnauthorizedError(response)

        self.username = username.text
        self.app_data = json.loads(parser.find("body").get("data-app-data")) # type: ignore
        self.id = self.app_data["userId"] # type: ignore
        self.csrf_token = self.app_data["csrf-token"] # type: ignore

        active_sales = parser.find("span", {"class": "badge badge-trade"})
        self.active_sales = int(active_sales.text) if active_sales else 0

        active_purchases = parser.find("span", {"class": "badge badge-orders"})
        self.active_purchases = int(
            active_purchases.text) if active_purchases else 0

        cookies = response.cookies.get_dict()
        if update_phpsessid or not self.phpsessid:
            self.phpsessid = cookies["PHPSESSID"]

        self.last_update = int(time.time())
        self.html = html_response
        self.__initiated = True
        return self

    def get_lot_fields(self, lot_id: int) -> LotFields:
        """
        Получает все поля лота.

        :param lot_id: ID лота.
        :type lot_id: :obj:`int`

        :return: объект с полями лота.
        :rtype: :class:`FunPayAPI.types.LotFields`
        """
        if not self.is_initiated:
            raise AccountNotInitiatedError()
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "x-requested-with": "XMLHttpRequest",
        }
        response = self.method("get", f"lots/offerEdit?offer={lot_id}", headers, {}, raise_not_200=True)

        bs = BeautifulSoup(response.text, "html.parser")

        result = {"active": "", "deactivate_after_sale": ""}
        result.update({field["name"]: field.get("value") or "" for field in bs.find_all("input")
                       if field["name"] not in ["active", "deactivate_after_sale"]})
        result.update({field["name"]: field.text or "" for field in bs.find_all("textarea")})
        result.update({field["name"]: field.find("option", selected=True)["value"] for field in bs.find_all("select")})
        result.update({field["name"]: "on" for field in bs.find_all("input", {"type": "checkbox"}, checked=True)})
        return LotFields(lot_id, result)
    
    @property
    def is_initiated(self) -> bool:
        """
        Инициализирован ли класс :class:`FunPayAPI.account.Account` с помощью метода :meth:`FunPayAPI.account.Account.get`?

        :return: :obj:`True`, если да, :obj:`False`, если нет.
        :rtype: :obj:`bool`
        """
        return self.__initiated
    


