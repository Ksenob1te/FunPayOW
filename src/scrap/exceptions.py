import requests

class RequestFailedError(Exception):
    """
    Исключение, которое возбуждается, если статус код ответа != 200.
    """
    def __init__(self, response: requests.Response):
        """
        :param response: объект ответа.
        """
        self.response = response
        self.status_code = response.status_code
        self.url = response.request.url
        self.request_headers = response.request.headers
        if "cookie" in self.request_headers:
            self.request_headers["cookie"] = "HIDDEN"
        self.request_body = response.request.body
        self.log_response = False

    def short_str(self):
        return f"Ошибка запроса к {self.url}. (Статус-код: {self.status_code})"

    def __str__(self):
        msg = f"Ошибка запроса к {self.url} .\n" \
              f"Метод: {self.response.request.method} .\n" \
              f"Статус-код ответа: {self.status_code} .\n" \
              f"Заголовки запроса: {self.request_headers} .\n" \
              f"Тело запроса: {self.request_body} ."
        if self.log_response:
            msg += f"\n{self.response.content.decode()}"
        return msg
    
class UnauthorizedError(RequestFailedError):
    """
    Исключение, которое возбуждается, если не удалось найти идентифицирующий аккаунт элемент и / или произошло другое
    событие, указывающее на отсутствие авторизации.
    """
    def __init__(self, response):
        super(UnauthorizedError, self).__init__(response)

    def short_str(self):
        return "Не авторизирован (возможно, введен неверный golden_key?)."
    
class AccountNotInitiatedError(Exception):
    """
    Исключение, которое возбуждается, если предпринята попытка вызвать метод класса :class:`FunPayAPI.account.Account`
    без предварительного получения данных аккаунта с помощью метода :meth:`FunPayAPI.account.Account.get`.
    """
    def __init__(self):
        pass

    def __str__(self):
        return "Необходимо получить данные об аккаунте с помощью метода Account.get()"