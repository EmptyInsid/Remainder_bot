import requests


class TelegramClient:
    '''Класс телеграмм-клиента для отправки сообщений администратору'''
    def __init__(self, token: str, base_url: str, admin_id: str):
        self.token = token
        self.base_url = base_url
        self.admin_id = admin_id

    def prepare_url(self, method: str) -> str:
        '''
        Подготовка url адреса для отправки запроса

        :param method: имя метода для выполнения
        :return: строка url
        '''

        result_url = f'{self.base_url}/bot{self.token}/'
        if method is not None:
            result_url += method
        return result_url

    def post(self, method: str = None, params: dict = None, data: dict = None):
        '''
        Отправки запроса

        :param method: имя метода для выполнения
        :param params: параметры запроса
        :param data: данные запроса
        :return: json запроса
        '''

        url = self.prepare_url(method)
        resp = requests.post(url, params=params, data=data)
        return resp.json()

    def send_message_to_admin(self, text) -> None:
        '''
        Отправка сообщения в чат администратору
        :param text: текст сообщения
        '''

        self.post(method='sendMessage', params={'text': text, 'chat_id': self.admin_id})
