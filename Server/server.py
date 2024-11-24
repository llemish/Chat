import selectors
import socket
import logging
import sys

from config_reader import ConfigReader
from user import User
from message import Message


class Server:

    """
    Класс реализующий работу сервера.
    Требует корректного указания пути к файлу конфигурации при запуске файла
    """

    def __init__(self):
        # Чтение файла конфигурации
        path_to_file = sys.argv[1]
        self._config = ConfigReader(path_to_file)
        logg_level = self._get_logg_level()

        # Инициализация логирования
        logging.basicConfig(level=logg_level, filename='syslog.log', filemode='a',
                            format="%(asctime)s:%(module)s:%(levelname)s:%(message)s")

        self._users = dict()
        self._sel = selectors.DefaultSelector()

        self._run_server()

    def _get_logg_level(self):
        level = logging.DEBUG
        if self._config.logging_level == 'INFO':
            level = logging.INFO
        elif self._config.logging_level == 'WARNING':
            level = logging.WARNING
        elif self._config.logging_level == 'ERROR':
            level = logging.ERROR
        elif self._config.logging_level == 'CRITICAL':
            level = logging.CRITICAL
        return level

    def _run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.bind(('', self._config.port))
            server_sock.listen(5)
            logging.debug('Server started')
            self._sel.register(server_sock, selectors.EVENT_READ, self._new_connection)

            # Опрос в цикле сокетов готовых к обработке
            while True:
                logging.debug("Waiting for connections or data...")
                events = self._sel.select()
                for key, mask in events:
                    callback = key.data
                    try:
                        success = callback(key.fileobj)
                        if not success:
                            self._delete_user(key.fileobj)
                    except OSError:
                        logging.warning(f'Client {key.fileobj} suddenly disconnected!')
                        sock = key.fileobj
                        self._sel.unregister(sock)
                        if sock in self._users:
                            del self._users[sock]

    def _new_connection(self, server_sock):
        # Обработка нового подключения
        sock, addr = server_sock.accept()
        if len(self._users) < self._config.max_user:
            self._sel.register(sock, selectors.EVENT_READ, self._get_user_message)
            logging.debug(f'New connection from {addr}')
            new_user = User('noname')
            new_user.sock = sock
            self._users[new_user.sock] = new_user
        else:
            logging.info(f'Too many users, connection denied')
            sock.sendall('Достигнуто предельное количество пользователей!'.encode())
            sock.close()
        return True

    def _get_user_message(self, sock):
        # Обработка сообщения пользователя
        addr = sock.getpeername()
        logging.debug(f'Get new message from {addr}')

        # Чтение из сокета
        try:
            data = sock.recv(1024)
        except ConnectionError:
            logging.warning(f'Client {addr} suddenly closed')
            return False
        logging.debug(f'Received {data} from {addr}')

        # Обработка полученных данных
        new_data = self._handle_message(data, sock)
        if not new_data:
            return False

        # Отправка сообщения пользователю
        success = self._send_message(sock, new_data)
        return success

    def _delete_user(self, sock):
        logging.info(f'Delete user from socket {sock}')
        del self._users[sock]
        self._sel.unregister(sock)

    def _get_user_names(self):
        names = [self._users[user].name for user in self._users if self._users[user].name != 'noname']
        return names

    def _send_message(self, sock, data):
        #  Отправка сообщения
        addr = sock.getpeername()
        logging.debug(f'Send {data} to {addr}')
        if isinstance(data, str):
            data = '\n\t\t\t\t\t' + data
            data = data.encode()
        elif isinstance(data, bytes):
            data = b'\n\t\t\t\t\t' + data

        try:
            sock.sendall(data)
        except ConnectionError:
            logging.warning(f'Client {addr} suddenly closed')
            return False
        return True

    def _handle_message(self, data, sock):
        #  Обработка сообщения
        message = Message(data)

        if not message.is_correct:
            return 'Неверный формат сообщения или команды'.encode()

        if message.is_command:
            new_data = self._command_handler(message.target_user, message.message, sock)
        else:
            success = self._send_message_to_user(message.target_user, message.message, sock)
            if success:
                new_data = f'Сообщение отправлено {message.target_user}'
            else:
                new_data = f'Не удалось отправить сообщение {message.target_user}'
        return new_data.encode()

    def _command_handler(self, command, parameter, sock):
        #  обработка команды
        new_data = f'Команда {command} не найдена'
        if command == 'init':
            new_data = str(self._config.max_message_length)
        elif command in ['registration', 'change_name']:
            name = parameter
            names = self._get_user_names()
            if name in names:
                new_data = 'Имя занято, выберите другое'
            elif name[:2] == '*/':
                new_data = 'Имя не может начинаться с "*/"'
            else:
                self._users[sock].name = name
                new_data = f'Имя успешно сменено на {name}'
        elif command == 'who':
            names = self._get_user_names()
            new_data = f'Доступные пользователи: {names}'
        elif command == 'exit':
            new_data = 'Bye!'
            self._delete_user(sock)
        return new_data

    def _send_message_to_user(self, target_user, message, sock):
        target_socket = None
        for key in self._users:
            if self._users[key].name == target_user:
                target_socket = self._users[key].sock
                break
        if target_socket is None:
            return False

        message = f'Сообщение от {self._users[sock].name}: {message}'
        success = self._send_message(target_socket, message)

        return success

s = Server()
