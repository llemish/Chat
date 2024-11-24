import socket
from dataclasses import dataclass
import selectors
from time import sleep
import sys


@dataclass
class ClientInfo:
    """

    Класс для хранения базовых настроек клиента
    HOST - ip-адрес сервера
    PORT - порт сервера для подключения
    MESSAGE_LENGTH - максимальная длина сообщения
    COMMANDS - перечень доступных пользователю команд

    """

    HOST = '127.0.0.1'
    PORT = 54321
    MESSAGE_LENGTH = 140
    COMMANDS = {'*/change_name: новое_имя': 'Изменить имя пользователя',
                '*/who': 'Узнать доступных пользователей',
                '*/exit': 'Отключиться и выйти',
                '*/help': 'Узнать доступные команды'}


class Client:

    def __init__(self):
        self._name = 'noname'
        self._max_message_length = ClientInfo.MESSAGE_LENGTH
        self._connection_flag = False
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        with self._sock:
            try:
                self._sock.connect((ClientInfo.HOST, ClientInfo.PORT))
                success = self._handshake()
                if success:
                    self._handle_connection()
            except ConnectionRefusedError:
                print(f'Сервер по адресу {ClientInfo.HOST} порт {ClientInfo.PORT} недоступен!')

    def _help(self):

        # Вывод перечня доступных команд
        print('Доступные команды:')
        for command in ClientInfo.COMMANDS:
            print('\t' + command + ' - ' + ClientInfo.COMMANDS[command])

    def _handshake(self):

        # Подключение к серверу и регистрация пользователя
        success = self._send('*/init')
        if not success:
            return False
        message = self._read()
        if not message:
            return False
        if message == 'Достигнуто предельное количество пользователей!':
            print(message)
            return False
        self._max_message_length = int(message)
        print(f'Соединение установлено. Максимальная длина сообщения: {self._max_message_length}')
        self._help()

        # Получение списка доступных пользователей
        success = self._send('*/who')
        if not success:
            return False
        message = self._read()
        if not message:
            return False
        print(message)

        # Регистрация на сервере
        flag = True
        name = input('Введите Ваше имя: ')
        while flag:
            self._send('*/registration:' + name)
            message = self._read()
            if name in message:
                flag = False
            else:
                print(message)
                name = input('Введите Ваше имя: ')
        self._name = name
        self._connection_flag = True
        print('Вы успешно зарегистрированы')
        print('Для отправки сообщения используйте следующий формат:')
        print('Имя_пользователя: текст_сообщения')
        return True

    def _handle_connection(self):
        #  Селектор выбирающий между получением сообщений от сервера и вводом пользователя
        sel = selectors.DefaultSelector()
        sel.register(sys.stdin, selectors.EVENT_READ, self._on_input_read)
        sel.register(self._sock, selectors.EVENT_READ, self._on_sock_read)

        while self._connection_flag:
            events = sel.select()
            for key, mask in events:
                callback = key.data
                callback()
            sleep(0.5)

        # Завершение работы программы
        sel.unregister(self._sock)
        self._sock.close()
        sel.unregister(sys.stdin)
        sel.close()

    def _send(self, message):
        # Отправка сообщения на сервер
        if len(message) > self._max_message_length:
            print('Превышена максимальная длина сообщения!')
            return False
        message_byte = message.encode()
        try:
            self._sock.sendall(message_byte)
        except ConnectionError:
            print('Сервер недоступен')
            self._connection_flag = False
            return False
        return True

    def _read(self):
        # Чтение данных от сервера
        try:
            message_bytes = self._sock.recv(self._max_message_length)
        except ConnectionError:
            print('Сервер неожиданно прервал соединение')
            self._connection_flag = False
            return False
        message = message_bytes.decode()
        return message

    def _on_input_read(self):
        # Обработка данных введённых пользователем
        try:
            data = input()
            if data == '*/help':
                self._help()
            else:
                if data == '*/exit':
                    self._connection_flag = False
                self._send(data)
        except UnicodeDecodeError:
            print('Ошибка ввода, попробуйте ввести сообщение ещё раз')

    def _on_sock_read(self):
        # Получение сообщения от сервера
        data = self._read()
        if data:
            print(data)


user = Client()
