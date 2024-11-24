class User:
    """
    Класс для хранения данных пользователей
    name - хранит имя пользователя
    sock - хранит ссылку на сокет пользователя
    """

    def __init__(self, name):
        self._name = name
        self._registered = False
        self._sock = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
        self._registered = True

    @property
    def sock(self):
        return self._sock

    @sock.setter
    def sock(self, sock):
        self._sock = sock
